#!/usr/bin/env python3
"""Start one new, isolated collection session; never reopen an existing game."""
import argparse
import fcntl
import json
import os
import time
from play_broker import Game, ROOT, now, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('game_id')
    parser.add_argument('--hours', type=float, default=12)
    args = parser.parse_args()
    config = json.loads(open(args.config).read())
    item, = [g for g in config['games'] if g['game_id'] == args.game_id]
    lock = (ROOT / 'control' / (item['game_id'] + '-broker.lock')).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    status_path = ROOT / 'control' / (item['game_id'] + '-broker-status.json')
    # Game requires a nonexistent directory, so prior evidence is never reset.
    game = Game(item)
    write_json(status_path, dict(pid=os.getpid(), engine_pid=game.proc.pid,
               state='running', session_id=game.session, started_at=now()))
    try:
        end = time.monotonic() + args.hours * 3600
        while time.monotonic() < end and not game.done:
            if (ROOT / 'control' / 'stop-broker').exists():
                break
            if (ROOT / 'control' / ('stop-' + game.gid + '-broker')).exists():
                break
            game.poll()
            time.sleep(0.15)
        # Workers make explicit saves at normal prompts. An unsolicited timer
        # must not inject SAVE into a game's question or keypress interlude.
    finally:
        game.close_engine()
        write_json(status_path, dict(pid=os.getpid(), state='stopped',
                   session_id=game.session, stopped_at=now(),
                   ending_claimed=game.done, last_event_index=game.index))


if __name__ == '__main__':
    main()
