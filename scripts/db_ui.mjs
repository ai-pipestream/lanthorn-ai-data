#!/usr/bin/env node
// Lanthorn collection DB browser: zero-dependency read-only UI over Postgres.
// Serves on the tailnet IP so it is reachable from anywhere on the tailnet.
import { execFile } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { homedir } from 'node:os';
import { join } from 'node:path';

const HOST = process.env.LANTHORN_UI_HOST || '100.110.72.95';
const PORT = Number(process.env.LANTHORN_UI_PORT || 5871);
const PW = readFileSync(join(homedir(), '.config/lanthorn/pg.env'), 'utf8')
  .split('\n').find(l => l.startsWith('POSTGRES_PASSWORD=')).split('=')[1].trim();

function sql(query) {
  return new Promise((resolve, reject) => {
    execFile('docker', ['exec', '-i', '-e', `PGPASSWORD=${PW}`, 'lanthorn-db',
      'psql', '-U', 'lanthorn', '-d', 'lanthorn', '-tAc', query],
      { maxBuffer: 64 * 1024 * 1024 }, (err, stdout, stderr) => {
        if (err) reject(new Error(stderr || err.message));
        else resolve(stdout.trim() ? JSON.parse(stdout.trim()) : null);
      });
  });
}

const okId = id => /^[a-z0-9-]+$/.test(id || '');

const PAGE = `<!doctype html><meta charset=utf-8><title>lanthorn progress</title>
<style>
body{font:14px system-ui;margin:2rem;background:#101418;color:#dde3ea}
input{padding:.4rem .7rem;width:22rem;background:#1b222b;color:#dde3ea;border:1px solid #38424e;border-radius:6px}
table{border-collapse:collapse;margin-top:1rem;width:100%}
th,td{padding:.3rem .6rem;border-bottom:1px solid #262e38;text-align:left;white-space:nowrap}
th{cursor:pointer;color:#8ab4f8}tr:hover td{background:#182029}
a{color:#8ab4f8;text-decoration:none}.n{color:#9aa4b0}.keep{color:#7dd87d}
h1{font-size:1.2rem}#sum{color:#9aa4b0;margin-top:.5rem}
</style>
<h1>lanthorn collection progress</h1>
<div id=sum></div>
<p><input id=q placeholder="filter games… (e.g. ready, complete, zork)" oninput="draw()">
<table id=t></table>
<script>
let rows=[];
fetch('/api/progress').then(r=>r.json()).then(d=>{rows=d;draw()});
function esc(s){return String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function draw(){
  const q=document.getElementById('q').value.toLowerCase();
  const ks=['game_id','title','sessions','events','cases','fleet_states','verdicts','last_event_at'];
  const f=rows.filter(r=>!q||ks.some(k=>String(r[k]??'').toLowerCase().includes(q)));
  const done=rows.filter(r=>(r.fleet_states||'').includes('complete')).length;
  document.getElementById('sum').textContent=
    rows.length+' catalog games — '+done+' completed, '+f.length+' shown. Click a game for detail.';
  let h='<tr>'+ks.map(k=>'<th onclick="sortBy(\\''+k+'\\')">'+k+'</th>').join('')+'</tr>';
  for(const r of f){
    h+='<tr>'+ks.map(k=>{
      let v=r[k]; if(k==='last_event_at')v=(v||'').slice(0,16).replace('T',' ');
      if(k==='game_id')return '<td><a href="/game?id='+esc(v)+'">'+esc(v)+'</a>';
      if(k==='verdicts')return '<td class="keep">'+esc(v||'')+'</td>';
      return '<td class="'+(typeof v==='number'?'':'n')+'">'+esc(v??'')+'</td>';
    }).join('')+'</tr>';
  }
  document.getElementById('t').innerHTML=h;
}
let sk='',sd=1;
function sortBy(k){sd=sk===k?-sd:1;sk=k;rows.sort((a,b)=>((a[k]??'')>(b[k]??'')?1:-1)*sd);draw()}
</script>`;

const GAME = `<!doctype html><meta charset=utf-8><title>game</title>
<style>body{font:14px system-ui;margin:2rem;background:#101418;color:#dde3ea;max-width:70rem}
pre{background:#182029;padding:.8rem;border-radius:8px;overflow:auto;font-size:12px}
h1{font-size:1.1rem}h2{font-size:.95rem;color:#8ab4f8;margin-top:1.4rem}
a{color:#8ab4f8}.n{color:#9aa4b0}</style>
<h1 id=t></h1><div id=m class=n></div>
<h2>runs</h2><pre id=r></pre><h2>judgments</h2><pre id=j></pre>
<h2>latest events</h2><pre id=e></pre><p><a href="/">&larr; all games</a>
<script>
const id=new URLSearchParams(location.search).get('id');
fetch('/api/game?id='+id).then(r=>r.json()).then(d=>{
  document.getElementById('t').textContent=(d.title||d.game_id)+'  ('+d.game_id+')';
  document.getElementById('m').textContent=[d.engine,d.source_batch,(d.fleet_states||[]).join(' | ')].filter(Boolean).join('  ·  ');
  const f=o=>JSON.stringify(o,null,1);
  document.getElementById('r').textContent=(d.runs||[]).map(r=>
    r.session_id+'  ev='+r.events+' cmd='+r.commands+' branches='+r.branches+(r.ending_claimed?'  ENDING CLAIMED':'')).join('\\n')||'no runs';
  document.getElementById('j').textContent=(d.judgments||[]).map(j=>j.judgment_id+': '+j.verdict+' — '+j.reason).join('\\n\\n')||'no judgments';
  document.getElementById('e').textContent=(d.events||[]).map(e=>
    (e.event_type==='command'?'> '+e.command:'  '+String(e.response||'').slice(0,180))).join('\\n')||'no events';
});
</script>`;

createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://x');
    if (url.pathname === '/') return res.end(PAGE);
    if (url.pathname === '/game') return res.end(GAME);
    if (url.pathname === '/api/progress') {
      const rows = await sql('SELECT json_agg(row_to_json(game_progress)) FROM game_progress');
      res.setHeader('content-type', 'application/json');
      return res.end(JSON.stringify(rows || []));
    }
    if (url.pathname === '/api/game') {
      const id = url.searchParams.get('id');
      if (!okId(id)) { res.statusCode = 400; return res.end('bad id'); }
      const [cat] = await sql(`SELECT json_agg(row_to_json(catalog)) FROM catalog WHERE game_id='${id}'`) || [{}];
      const runs = await sql(`SELECT json_agg(row_to_json(t)) FROM (SELECT * FROM run_summary WHERE replace(game_id,'-kimi','')='${id}' ORDER BY last_event_at DESC) t`);
      const judgments = await sql(`SELECT json_agg(record ORDER BY judgment_id) FROM judgments WHERE replace(game_id,'-kimi','')='${id}'`);
      const events = await sql(`SELECT json_agg(row_to_json(t)) FROM (SELECT event_type, command, response FROM events WHERE replace(game_id,'-kimi','')='${id}' ORDER BY timestamp_utc_ms DESC, event_index DESC LIMIT 40) t`);
      const fleet = await sql(`SELECT json_agg(row_to_json(fleet_state)) FROM fleet_state WHERE replace(game_id,'-kimi','')='${id}'`);
      res.setHeader('content-type', 'application/json');
      return res.end(JSON.stringify({ ...(cat || {}), runs, judgments,
        events: (events || []).reverse(), fleet_states: (fleet || []).map(f => `${f.game_id}:${f.cli || 'muse'}:${f.state}`) }));
    }
    res.statusCode = 404; res.end('not found');
  } catch (e) {
    res.statusCode = 500; res.end(String(e.message || e));
  }
}).listen(PORT, HOST, () => console.log(`lanthorn-ui on http://${HOST}:${PORT}`));
