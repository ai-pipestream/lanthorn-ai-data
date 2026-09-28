"""Regression checks against real subprocess pipes, not mocked readiness."""
import json
import selectors
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from play_broker import Game


class TransportTest(unittest.TestCase):
    def fixture(self, code, timeout=3):
        temp = tempfile.TemporaryDirectory(prefix='lanthorn-transport-')
        self.addCleanup(temp.cleanup)
        game = Game.__new__(Game)
        game.config = {'response_timeout_seconds': timeout}
        game.base = Path(temp.name)
        game.session = 'transport-test'
        game.gid = 'transport-test'
        game.branch = game.index = 0
        game.story_sha = 'test'
        game.rows = {}
        game.unresolved_input = None
        game.journal = (game.base / 'events.jsonl').open('a')
        game.raw = (game.base / 'stdout.raw').open('ab', buffering=0)
        game.stderr = (game.base / 'stderr').open('ab')
        game.proc = subprocess.Popen([sys.executable, '-u', '-c', code], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=game.stderr)
        game.selector = selectors.DefaultSelector()
        game.selector.register(game.proc.stdout, selectors.EVENT_READ)
        self.addCleanup(game.journal.close)
        self.addCleanup(game.raw.close)
        self.addCleanup(game.close_engine)
        return game

    def test_quiet_fragment_is_not_input_readiness(self):
        game = self.fixture("import sys,time\nprint('first',flush=True)\nend=time.monotonic()+0.9\nwhile time.monotonic()<end: pass\nprint('second >',flush=True)\nsys.stdin.readline()")
        start = time.monotonic()
        data, state = game.drain()
        self.assertGreater(time.monotonic() - start, .9)
        self.assertEqual(data, b'first\nsecond >\n')
        self.assertEqual(state, 'awaiting_input_or_idle')

    def test_timeout_blocks_command_and_checkpoint_without_writing(self):
        game = self.fixture("import sys,time\nprint('ready >',flush=True)\ncommand=sys.stdin.readline()\nend=time.monotonic()+1.8\nwhile time.monotonic()<end: pass\nprint('done '+command.strip()+' >',flush=True)\nnext_command=sys.stdin.readline()\nprint('next '+next_command.strip()+' >',flush=True)\nsys.stdin.readline()")
        self.assertEqual(game.drain()[1], 'awaiting_input_or_idle')
        game.config['response_timeout_seconds'] = .4
        first = game.send('look', {'origin': 'exploration'})
        self.assertEqual(first['engine_state'], 'no_output_timeout')
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            game.send('north', {})
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            game.handle({'action':'restore','name':'blocked'})
        self.assertEqual(game.branch, 0)
        game.config['response_timeout_seconds'] = 3
        delayed = game.handle({'action':'await_output'})['event']
        self.assertEqual(delayed['metadata']['delayed_for_event_id'], first['event_id'])
        self.assertEqual(delayed['response'], 'done look >\n')
        self.assertIsNone(game.unresolved_input)
        next_row = game.send('inventory', {})
        self.assertEqual(next_row['response'], 'next inventory >\n')

    def test_exited_engine_is_not_a_prompt(self):
        game = self.fixture("print('goodbye',flush=True)")
        data, state = game.drain()
        self.assertEqual(data, b'goodbye\n')
        self.assertEqual(state, 'engine_exited')


if __name__ == '__main__':
    unittest.main()
