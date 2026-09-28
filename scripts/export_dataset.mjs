import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const events = [];
for (const entry of await fs.readdir(path.join(root, 'play'), {withFileTypes:true})) {
  if (!entry.isDirectory()) continue;
  const source = path.join(root, 'play', entry.name, 'events.jsonl');
  let text;
  try { text = await fs.readFile(source, 'utf8'); } catch { continue; }
  const lines = text.split('\n');
  // Ignore only a trailing partial append; malformed completed records are errors.
  for (const line of lines.slice(0, -1)) if (line.trim()) events.push(JSON.parse(line));
}
const byId = new Map(events.map(e=>[e.event_id,e]));
let review={cases:{}};
try { review=JSON.parse(await fs.readFile(path.join(root,'reviewed','fullplay-cases.json'),'utf8')); } catch {}
const transportBad=new Set();
try {
  const manual=JSON.parse(await fs.readFile(path.join(root,'reviewed','transport-events.json'),'utf8'));
  for(const entry of manual.events||[]) transportBad.add(entry.event_id);
} catch(error) { if(error.code!=='ENOENT') throw error; }
const pending=new Set();
for(const e of events) {
  // A save/restore can receive buffered output too. Only interpreter input
  // records consume the pending-output marker; annotations and hints cannot.
  if(e.event_type==='delayed_output') {
    transportBad.add(e.event_id);
    if(e.metadata?.delayed_for_event_id) transportBad.add(e.metadata.delayed_for_event_id);
    if(e.engine_state!=='no_output_timeout') pending.delete(e.session_id);
    continue;
  }
  if(e.command == null) continue; // Empty Enter is an actual input, unlike metadata.
  if(pending.has(e.session_id)) { transportBad.add(e.event_id); pending.delete(e.session_id); }
  if(e.engine_state==='no_output_timeout') { transportBad.add(e.event_id); pending.add(e.session_id); }
}

const headers = ['event_id','game_id','session_id','branch_id','event_index','timestamp_utc_ms','event_type','origin','case_id','intent','command','response','expected_outcome','help_reason','hint_text','hint_source','related_event_ids','review_status','transport_quality','story_sha256'];
const rows = events.map(e => {
  const m=e.metadata||{};
  return [e.event_id,e.game_id,e.session_id,e.branch_id,e.event_index,new Date(e.timestamp).toISOString(),e.event_type,m.origin||'',m.case_id||'',m.intent||'',e.command||'',e.response,m.expected_outcome||'',m.reason||'',m.hint_text||'',m.hint_source||'',JSON.stringify(m.related_event_ids||m.event_ids||[]),e.review_status,transportBad.has(e.event_id)?'quarantine_delayed_output':'captured',e.story_sha256];
});
const caseHeaders=['annotation_event_id','case_id','game_id','session_id','failed_event_id','corrected_event_id','failed_branch_id','corrected_branch_id','intent','failed_command','failure_response','corrected_command','correction_response','failure_type','suggestion','intent_preserved','outcome_label','synthetic_probe','evidence_available','review_status','review_notes','notes','story_sha256'];
const cases=[];
for (const e of events.filter(e=>e.event_type==='annotation')) {
  const m=e.metadata||{}, before=byId.get(m.failed_event_id), after=byId.get(m.corrected_event_id);
  const proposed=review.cases?.[e.event_id] ?? review.cases?.[`${e.game_id}:${m.case_id}`];
  const refs=[m.failed_event_id,m.corrected_event_id].filter(Boolean);
  const exactRefs=[...new Set(refs)];
  const proposedRefs=[...new Set(proposed?.evidence_event_ids||[])];
  const verdict=proposed && exactRefs.length && exactRefs.length===proposedRefs.length && exactRefs.every(id=>proposedRefs.includes(id)) ? proposed : null;
  const bad=transportBad.has(before?.event_id)||transportBad.has(after?.event_id);
  cases.push([e.event_id,m.case_id||'',e.game_id,e.session_id,m.failed_event_id||'',m.corrected_event_id||'',before?.branch_id||'',after?.branch_id||'',m.intent||'',before?.command||'',before?.response||'',after?.command||'',after?.response||'',m.failure_type||'',m.suggestion||'',m.intent_preserved||'uncertain',m.observed_outcome||'uncertain',m.synthetic_probe===true,Boolean(before&&after&&before.game_id===e.game_id&&after.game_id===e.game_id),bad?'quarantine':(verdict?.status||'unreviewed'),bad?'Delayed/interleaved output; not an isolated command-response pair':(verdict?.notes||''),m.notes||'',e.story_sha256]);
}

// Artifact Tool supplies typed table authoring and value verification. The public
// API has CSV import but no documented CSV export, so serialize verified values.
const book=Workbook.create();
const outputs=[['Events',headers,rows,'events.csv'],['Cases',caseHeaders,cases,'test-cases.csv']];
await fs.mkdir(path.join(root,'exports'),{recursive:true});
for (const [name,cols,data] of outputs) {
  const sheet=book.worksheets.add(name);
  const matrix=[cols,...data];
  // Literal values only. No formulas are introduced into this test corpus.
  sheet.getRangeByIndexes(0,0,matrix.length,cols.length).setNumberFormat('@');
  // Shield every string from automatic date/formula interpretation. Remove
  // this reversible marker after the artifact readback, before CSV writing.
  sheet.getRangeByIndexes(0,0,matrix.length,cols.length).values=matrix
    .map(row=>row.map(value=>typeof value==='string' ? 'literal:'+value : value));
}
book.recalculate();
for (const [name,cols,data,filename] of outputs) {
  const got=book.worksheets.getItem(name).getRangeByIndexes(0,0,data.length+1,cols.length).values
    .map(row=>row.map(value=>typeof value==='string' && value.startsWith('literal:') ? value.slice(8) : value));
  const expected=[cols,...data];
  if (JSON.stringify(got)!==JSON.stringify(expected)) { for(let r=0;r<expected.length;r++) for(let c=0;c<cols.length;c++) if(got[r][c]!==expected[r][c]) throw Error(`${name}: first change row ${r} col ${c}: expected ${JSON.stringify(expected[r][c])}, got ${JSON.stringify(got[r][c])}`); }
  const quote=value=>'"'+String(value??'').replaceAll('"','""')+'"';
  const csv=got.map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
  const target=path.join(root,'exports',filename);
  await fs.writeFile(target+'.tmp',csv,'utf8');
  await fs.rename(target+'.tmp',target);
}
const status={exported_at:new Date().toISOString(),events:rows.length,cases:cases.length,review_status:'unreviewed',purpose:'Synthetic test data, not a measure of model playing skill',files:outputs.map(x=>x[3])};
await fs.writeFile(path.join(root,'exports','status.json'),JSON.stringify(status,null,2)+'\n');
console.log(JSON.stringify(status));
