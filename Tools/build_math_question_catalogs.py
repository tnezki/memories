#!/usr/bin/env python3
"""Regenerate derived math worksheet catalogs from canonical family files.

Run from the memories repo root. No network access or third-party packages required.
Canonical edit points:
  _question_structure/catalogs/math_question_family_registry.json
  _question_structure/catalogs/math_course_family_maps.json
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
REG_PATH=ROOT/'_question_structure/catalogs/math_question_family_registry.json'
MAP_PATH=ROOT/'_question_structure/catalogs/math_course_family_maps.json'
BANK_PATH=ROOT/'_question_structure/catalogs/math_worksheet_generator_bank.json'
CAT_PATH=ROOT/'district_tools/worksheet_builder/question_structure_catalog.json'

reg=json.loads(REG_PATH.read_text())
maps=json.loads(MAP_PATH.read_text())

if reg.get('schema')!='math-question-family-registry/1.0':
    raise SystemExit('unexpected family registry schema')
if maps.get('schema')!='math-course-family-maps/1.0':
    raise SystemExit('unexpected course-map schema')
if reg.get('default_wording_profile')!='direct_concise':
    raise SystemExit('math family registry must default to direct_concise')

required_family={'family_id','status','domain','label','evidence_job','student_action','default_wording_profile','response_modes','representation_modes','generator','quality_gates','source_basis'}
required_generator={'prompt_pattern','parameter_names','property_controls','validity_constraints','answer_rule','parallel_invariants','parallel_variation','difficulty_policy','workspace_default','render_route'}

family_list=reg.get('families') or []
ids=[]
for f in family_list:
    missing=required_family-set(f)
    if missing: raise SystemExit(f"{f.get('family_id','<unknown>')} missing family fields: {sorted(missing)}")
    fid=f['family_id']
    if not re.fullmatch(r'[A-Z0-9_]+',fid): raise SystemExit(f'invalid family_id: {fid}')
    if f['default_wording_profile'] not in ('direct_concise','standard','inverted','context_rich'):
        raise SystemExit(f'{fid}: invalid wording profile')
    if not f['response_modes'] or not f['representation_modes']:
        raise SystemExit(f'{fid}: empty response/representation modes')
    g=f['generator']
    gm=required_generator-set(g)
    if gm: raise SystemExit(f'{fid} missing generator fields: {sorted(gm)}')
    if not g['property_controls'] or not g['validity_constraints'] or not g['answer_rule']:
        raise SystemExit(f'{fid}: generator contract is underspecified')
    ids.append(fid)
if len(ids)!=len(set(ids)):
    dup=sorted({x for x in ids if ids.count(x)>1})
    raise SystemExit(f'duplicate family_id(s): {dup}')
families={f['family_id']:f for f in family_list}

course_names=[]
for c in maps.get('courses') or []:
    if c['name'] in course_names: raise SystemExit(f"duplicate course map: {c['name']}")
    course_names.append(c['name'])
    topic_ids=[]
    for t in c.get('topics') or []:
        if t['id'] in topic_ids: raise SystemExit(f"{c['name']}: duplicate topic id {t['id']}")
        topic_ids.append(t['id'])
        missing=[fid for fid in t.get('family_ids',[]) if fid not in families]
        if missing: raise SystemExit(f"{c['name']} / {t['id']} references missing families: {missing}")

def public(fid):
    f=families[fid]
    return {
        'id':fid,
        'category':f.get('category','Math'),
        'label':f['label'],
        'summary':f['evidence_job'],
        'representations':f['representation_modes'],
        'response_modes':f['response_modes'],
        'difficulty':['intro','standard','mastery'],
        **({'visual':f['generator']['render_route']} if f['generator']['render_route']!='html_mathjax' else {}),
        'wording_profile':f['default_wording_profile'],
        'quality_status':f['status']
    }

courses=[]
for c in maps['courses']:
    topics=[]
    for t in c['topics']:
        topics.append({'id':t['id'],'label':t['label'],'families':[public(fid) for fid in t['family_ids']]})
    courses.append({'name':c['name'],'default_topic':c['default_topic'],'topics':topics})

bank={
    'schema':'math-worksheet-generator-bank/0.1',
    'architecture_version':'math-family-contracts/1.0',
    'status':'CURRENT',
    'updated':reg['updated'],
    'authority':'Generated compatibility aggregate. Canonical definitions live in math_question_family_registry.json and math_course_family_maps.json.',
    'source_use_rule':reg['source_use_rule'],
    'default_wording_profile':reg['default_wording_profile'],
    'canonical_family_registry':'_question_structure/catalogs/math_question_family_registry.json',
    'canonical_course_maps':'_question_structure/catalogs/math_course_family_maps.json',
    'generator_rules':{
        'family_first':'Resolve an exact family contract before writing prose.',
        'no_freeform_drift':'Do not substitute a generic prompt for a selected family.',
        'concise_default':'Use direct_concise unless functional context is required.',
        'parameterize':'Create original parameters under the family contract and its property controls.',
        'parallel_forms':'Preserve family/evidence/difficulty slot-for-slot.',
        'qa':'Solve independently and verify representation/answer alignment.'
    },
    'courses':courses,
    'family_contracts':families
}
cat={
    'schema':'math-worksheet-question-structure-catalog/0.3-family-contracts',
    'status':'CURRENT',
    'updated':reg['updated'],
    'canonical_generator_bank':'_question_structure/catalogs/math_worksheet_generator_bank.json',
    'canonical_family_registry':'_question_structure/catalogs/math_question_family_registry.json',
    'canonical_course_maps':'_question_structure/catalogs/math_course_family_maps.json',
    'reference_model':{
        'purpose':'Browse canonical reusable math question families by course and topic.',
        'source_principles':['Teacher parallel forms inform recurring evidence architectures.','External worksheet catalogs inform coverage/property options only.','One family definition may be mapped to multiple courses.','Direct/concise wording is the worksheet default.'],
        'copyright_rule':reg['source_use_rule']
    },
    'parallel_form_policy':{
        'invariant':'Same family contract, evidence job, student action, response/representation role, and difficulty band.',
        'may_vary':['numbers','functional contexts','choice order','diagram values/orientation'],
        'must_not_drift':['target skill','reasoning demand','representation role','response demand','difficulty band']
    },
    'courses':courses,
    'generic_families':[]
}
BANK_PATH.write_text(json.dumps(bank,indent=2,ensure_ascii=False)+'\n')
CAT_PATH.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n')
print(f'OK: {len(families)} families, {len(courses)} active courses')
