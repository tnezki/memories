#!/usr/bin/env python3
"""Validate the canonical modular math-family library and regenerate derived worksheet catalogs.

Run from the memories repo root. No network or third-party packages required.
The canonical composition is declared in:
  _question_structure/catalogs/math_family_library_manifest.json
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
CROOT=ROOT/'_question_structure/catalogs'
MANIFEST=CROOT/'math_family_library_manifest.json'
BANK=CROOT/'math_worksheet_generator_bank.json'
CAT=ROOT/'district_tools/worksheet_builder/question_structure_catalog.json'

def load(p): return json.loads(p.read_text())
def resolve(rel):
    p=CROOT/(rel.split('catalogs/',1)[1] if rel.startswith('catalogs/') else rel)
    if not p.exists(): raise SystemExit(f'missing canonical math source: {p.relative_to(ROOT)}')
    return p
m=load(MANIFEST)
if m.get('schema')!='math-family-library-manifest/1.0': raise SystemExit('unexpected math family manifest schema')

required_family={'family_id','status','domain','label','evidence_job','student_action','default_wording_profile','response_modes','representation_modes','generator','quality_gates','source_basis'}
required_generator={'prompt_pattern','parameter_names','property_controls','validity_constraints','answer_rule','parallel_invariants','parallel_variation','difficulty_policy','workspace_default','render_route'}
all_families={}
for src in m['family_sources']:
    doc=load(resolve(src['path']))
    for f in doc.get('families',[]):
        fid=f.get('family_id')
        if not fid or not re.fullmatch(r'[A-Z0-9_]+',fid): raise SystemExit(f'invalid family id: {fid}')
        if fid in all_families: raise SystemExit(f'duplicate global family id: {fid}')
        missing=required_family-set(f)
        if missing: raise SystemExit(f'{fid} missing family fields {sorted(missing)}')
        gm=required_generator-set(f['generator'])
        if gm: raise SystemExit(f'{fid} missing generator fields {sorted(gm)}')
        all_families[fid]=f

courses=[]; course_names=set()
for src in m['course_map_sources']:
    doc=load(resolve(src['path']))
    source_courses=doc.get('courses')
    if source_courses is None:
        source_courses=[{'name':doc.get('course_label') or doc.get('course'),'default_topic':doc.get('topics',[{}])[0].get('id'),'topics':doc.get('topics',[])}]
    for c in source_courses:
        if c['name'] in course_names: raise SystemExit(f'duplicate course map: {c["name"]}')
        course_names.add(c['name'])
        topic_ids=set(); norm_topics=[]
        for t in c.get('topics',[]):
            if t['id'] in topic_ids: raise SystemExit(f'{c["name"]}: duplicate topic {t["id"]}')
            topic_ids.add(t['id'])
            missing=[fid for fid in t.get('family_ids',[]) if fid not in all_families]
            if missing: raise SystemExit(f'{c["name"]}/{t["id"]}: missing families {missing}')
            norm_topics.append({'id':t['id'],'label':t['label'],'family_ids':t.get('family_ids',[])})
        courses.append({'name':c['name'],'default_topic':c.get('default_topic') or (norm_topics[0]['id'] if norm_topics else None),'topics':norm_topics})

def public(fid):
    f=all_families[fid]; route=f['generator'].get('render_route')
    out={'id':fid,'category':f.get('category','Math'),'label':f['label'],'summary':f['evidence_job'],'representations':f['representation_modes'],'response_modes':f['response_modes'],'difficulty':['intro','standard','mastery'],'wording_profile':f['default_wording_profile'],'quality_status':f['status']}
    if route and route!='html_mathjax': out['visual']=route
    return out

public_courses=[]
for c in courses:
    public_courses.append({'name':c['name'],'default_topic':c['default_topic'],'topics':[{'id':t['id'],'label':t['label'],'families':[public(fid) for fid in t['family_ids']]} for t in c['topics']]})

bank={'schema':'math-worksheet-generator-bank/0.2-modular','architecture_version':'math-family-contracts/1.1-modular','status':'CURRENT','updated':m.get('updated'),'authority':'Derived compatibility aggregate. Canonical sources are resolved through math_family_library_manifest.json.','source_use_rule':m.get('source_use_rule'),'default_wording_profile':'direct_concise','canonical_family_library_manifest':'_question_structure/catalogs/math_family_library_manifest.json','generator_rules':{'family_first':'Resolve exact family before authoring.','no_freeform_drift':'Do not substitute a generic prompt for a selected family.','concise_default':'Use direct_concise unless functional context is required.','parameterize':'Generate original legal parameters under the family contract.','parallel_forms':'Preserve family/evidence/difficulty slot-for-slot.','refresh_candidates':'Create three independently solved same-family candidates per worksheet slot.','qa':'Verify prompt, representation, and answer alignment.'},'courses':public_courses,'family_contracts':all_families}
cat={'schema':'math-worksheet-question-structure-catalog/0.4-modular','status':'CURRENT','updated':m.get('updated'),'canonical_family_library_manifest':'_question_structure/catalogs/math_family_library_manifest.json','reference_model':{'purpose':'Browse canonical reusable math question families by course/topic.','source_principles':['Teacher parallel forms inform recurring evidence architecture.','External worksheet catalogs inform coverage/property options only.','Shared family definitions are referenced by ID across courses.','Direct/concise wording is the worksheet default.'],'copyright_rule':m.get('source_use_rule')},'parallel_form_policy':{'invariant':'Same family/evidence/student action/response-representation role/difficulty band.','may_vary':['numbers','functional contexts','choice order','diagram/data values and orientation'],'must_not_drift':['target skill','reasoning demand','representation role','response demand','difficulty band']},'courses':public_courses,'generic_families':[]}
BANK.write_text(json.dumps(bank,indent=2,ensure_ascii=False)+'\n')
CAT.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n')
print(f'OK: {len(all_families)} canonical families, {len(courses)} active courses')
