#!/usr/bin/env python3
"""Geometry canonical extraction tests. Synthetic offline CPM-like fixtures only."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import geometry_extract as g


def page(body):
    return '<!DOCTYPE html><html><body><div id="contents">' + body + '</div></body></html>'


def question(pid, body):
    return ('<div class="contentContainerReference problem" id="' + pid + '" container-id="source-geometry">'
            '<div class="contentContainerReference-title">' + pid + '.</div>'
            '<div class="contentContainerReference-body"><p>' + body + '</p></div></div>')


class GeometryExtractionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'geometry_source'
        self.root.mkdir()
        self.out = Path(self.tmp.name) / 'private_output'
        self.qa = {'errors': [], 'warnings': []}

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, folder, name, data):
        p = self.root / folder / name
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(data, encoding='utf-8')
        return p

    def extract(self, p):
        self.out.mkdir(exist_ok=True)
        return g.extract_page(p, self.root, self.out, set(), {}, self.qa)

    def test_toc_126_and_13_checkpoint_ids(self):
        self.assertEqual(sum(len(x.split()) for x in g.LESSONS.values()), 126)
        self.assertEqual(len(g.EXPECTED_CHECKPOINTS), 13)
        self.assertEqual(set(g.EXPECTED_CHECKPOINTS), {'1','2','3','4','5a','5b','6','7','8','9a','9b','10','11'})
        self.assertEqual(g.source_role(Path('ch08/CPM eBooks - CC Geometry Lesson 8.closure.html')), ('closure','8'))
        self.assertEqual(g.source_role(Path('ch04/CPM eBooks - CC Geometry Teacher Notes 4.closure.html')), ('teacher_closure','4'))
        self.assertEqual(g.source_role(Path('checkpoints/9b.html')), ('checkpoint','9b'))
        self.assertEqual(g.source_role(Path('standards/overview.html'))[0], 'standards')

    def test_closure_student_teacher_pair_and_self_reflection(self):
        p = self.add('ch02', 'CPM eBooks - CC Geometry Lesson 2.closure.html', page(
            question('CL 2-118','Compute the value.')
            + question('CL 2-119','Check your answers using the table at the end. Which problems do you feel confident about? Which problems were hard?')
            + '<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            + question('CL 2-118','Solution 42')
        ))
        cards = self.extract(p)
        probs = [c for c in cards if c['card_type'] == 'problem']
        sols = [c for c in cards if c['card_type'] == 'solution']
        self.assertEqual((len(probs), len(sols)), (2,1))
        self.assertEqual(probs[0]['paired_teacher_key_card_id'], sols[0]['card_id'])
        self.assertEqual(sols[0]['paired_student_card_id'], probs[0]['card_id'])
        self.assertEqual(sols[0]['visibility'], 'teacher_only')
        self.assertEqual(probs[1]['suggested_instructional_role'],'closure_self_assessment')
        self.assertIsNone(probs[1]['paired_teacher_key_card_id'])
        self.assertFalse(any(w['warning']=='closure_question_without_key' for w in self.qa['warnings']))

    def test_chapter_8_nested_student_and_solution_problem_wrappers(self):
        p = self.add('ch08','CPM eBooks - CC Geometry Lesson 8.closure.html', page(
            '<h3>4. WHAT HAVE I LEARNED?</h3><ul class="plain"><li>'
            + question('CL 8-130','Geometry original problem with drawing.')
            + question('CL 8-131','Check your answers using the table at the end of the closure section. Which problems were hard?')
            + '<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            + question('CL 8-130','Solution diagram.') + '</li></ul>'))
        cards = self.extract(p)
        self.assertEqual(len([c for c in cards if c['card_type']=='problem']),2)
        self.assertEqual(len([c for c in cards if c['card_type']=='solution']),1)
        self.assertEqual(len([c for c in cards if c['paired_student_card_id']]),1)
        self.assertFalse(any(w['warning'] in ('unmatched_or_ambiguous_teacher_key','closure_question_without_key') for w in self.qa['warnings']))

    def test_checkpoint_image_only_practice_with_original_answers_hidden(self):
        fld = self.root / 'checkpoints' / '7_files'
        fld.mkdir(parents=True)
        (fld/'first.png').write_bytes(b'fake image 1')
        (fld/'second.png').write_bytes(b'fake image 2')
        p = self.add('checkpoints','7.html',page(
            '<div class="row">Checkpoint 7 Problem 7-136</div>'
            '<p>Answers to Problem 7-136: 12</p>'
            '<p>Trigonometry introduction</p><div>Example 1: Solve this.</div><div>Solution: with steps</div>'
            '<p>Now we can go back and solve the original problems.</p><div>Original solution: 12</div>'
            '<p>Here are some more to try.</p><div class="row"><ol>'
            '<li><img src="./7_files/first.png"></li><li><img src="./7_files/second.png"></li></ol></div>'
            '<p>Answers:</p><div class="row">12, 27</div>'))
        cards = self.extract(p)
        practices = [c for c in cards if c['suggested_instructional_role']=='checkpoint_practice']
        self.assertEqual(len(practices), 2)
        self.assertEqual([c['source_list_item_number'] for c in practices],[1,2])
        self.assertTrue(all(c['visibility']=='student_candidate' for c in practices))
        self.assertTrue(all(c['source_problem_id'] is None for c in practices))
        self.assertTrue(all(len(c['media'])==1 and c['media'][0]['status']=='copied' for c in practices))
        self.assertTrue(all(c['text']=='' for c in practices))
        for c in practices:
            self.assertTrue((self.out/c['media'][0]['output_relative']).is_file())
        self.assertTrue(any(c['visibility']=='teacher_only' and 'Original solution' in c['text'] for c in cards))
        self.assertTrue(any(c['visibility']=='teacher_only' and c['text'].startswith('Answers:') for c in cards))
        self.assertTrue(any(c['visibility']=='student_candidate' and 'Solution: with steps' in c['text'] for c in cards))

    def test_teacher_notes_private(self):
        p = self.add('ch09','CPM eBooks - CC Geometry Teacher Notes 9.closure.html',page('<p>Teacher-only pedagogical guidance.</p>'))
        cards = self.extract(p)
        self.assertTrue(cards)
        self.assertTrue(all(c['visibility']=='teacher_only' for c in cards))

    def test_tex_media_and_source_canonical_identity(self):
        f = self.root/'ch01'/'CPM eBooks - CC Geometry Lesson 1.1.1_files'
        f.mkdir(parents=True)
        (f/'shape.png').write_bytes(b'fake geometry diagram')
        p = self.add('ch01','CPM eBooks - CC Geometry Lesson 1.1.1.html',page(question('1-1',
            '<c3po-media><script type="math/tex">\\sqrt{2}</script></c3po-media>'
            '<img src="./CPM eBooks - CC Geometry Lesson 1.1.1_files/shape.png">')))
        card = next(c for c in self.extract(p) if c['card_type']=='problem')
        self.assertEqual(card['course'],'geometry')
        self.assertEqual(card['source_problem_id'],'1-1')
        self.assertIn(r'\sqrt{2}',card['math_tex'])
        self.assertIn('assets/ch01',card['html'])
        self.assertEqual(card['media'][0]['status'],'copied')
        self.assertEqual(card['source_container_id'],'source-geometry')
        self.assertEqual(len(card['source_sha256']),64)

    def test_reject_outside_media_and_report_missing_images(self):
        p=self.add('ch01','CPM eBooks - CC Geometry Lesson 1.1.1.html',page(question('1-2',
            '<img src="./missing_files/shape.png"><img src="../../not-safe.png">')))
        c = next(c for c in self.extract(p) if c['card_type']=='problem')
        self.assertEqual([x['status'] for x in c['media']], ['missing_local_file','unsafe_outside_source'])

    def make_inventory(self):
        for ch,lessons in g.LESSONS.items():
            d=f'ch{ch:02d}'
            for lesson in lessons.split():
                self.add(d,f'CPM eBooks - CC Geometry Lesson {lesson}.html',page(question(f'{ch}-1','Sample problem')))
            for role in ('opening','closure'):
                self.add(d,f'CPM eBooks - CC Geometry Lesson {ch}.{role}.html',page('<p>Class reflection material.</p>'))
                self.add(d,f'CPM eBooks - CC Geometry Teacher Notes {ch}.{role}.html',page('<p>Teacher guidance.</p>'))
            (self.root/d/f'CCG Ch {ch} RPs.pdf').write_bytes(b'%PDF fake')
            parent=self.root/'parent_guides';parent.mkdir(exist_ok=True)
            (parent/f'CCG_PG_Ch{ch}.pdf').write_bytes(b'%PDF fake')
        for ch in g.EXPECTED_CHECKPOINTS:
            self.add('checkpoints',f'{ch}.html',page('<p>Checkpoint content.</p>'))
        self.add('checkpoints','CPM eBooks - CC Geometry Checkpoints.html',page('<p>Checkpoint index.</p>'))
        for x in ('overview.html','1.html','2.html','CPM eBooks - CC Geometry Standards.html'):
            self.add('standards',x,page('<p>Standards.</p>'))
        for n in range(4):
            (self.root/'standards'/f'standards_{n}.pdf').write_bytes(b'%PDF fake')
        for n in range(5):
            misc=self.root/'misc';misc.mkdir(exist_ok=True)
            (misc/f'misc_{n}.pdf').write_bytes(b'%PDF fake')
        for n in ('CCG_PG-algpractice_part1.pdf','CCG_PG-algpractice_part2.pdf','PG_intro_generic.pdf'):
            (self.root/'parent_guides'/n).write_bytes(b'%PDF fake')
        self.add('', 'CPM eBooks - CC Geometry Overview.html',page('<p>Overview.</p>'))
        self.add('', 'CPM eBooks - CC Geometry Table of Contents.html',page('<p>TOC.</p>'))
        for p in g.pages(self.root):
            p.with_name(p.stem+'_files').mkdir(exist_ok=True)

    def test_full_source_inventory_and_private_end_to_end(self):
        self.make_inventory()
        inv=g.inventory(self.root)
        self.assertEqual(inv['errors'],[])
        self.assertEqual(inv['missing_checkpoints'],[])
        self.assertEqual(inv['missing_parent_guides'],[])
        self.assertEqual(len(list(g.pages(self.root))),194)
        self.assertEqual(len(g.resources(self.root)),36)
        with contextlib.redirect_stdout(io.StringIO()):
            exitcode=g.run(['--source',str(self.root),'--output',str(self.out)])
        self.assertEqual(exitcode,0)
        report=json.loads((self.out/'qa_report.json').read_text())
        self.assertEqual(report['summary']['numbered_lessons_found'],126)
        self.assertEqual(report['summary']['source_pages'],194)
        self.assertEqual(report['summary']['indexed_reference_pdfs'],36)
        self.assertEqual(report['summary']['missing_media'],0)
        self.assertTrue((self.out/'GEOMETRY_GENERATED_OUTPUT.marker').is_file())
        self.assertTrue((self.out/'cards.jsonl').is_file())
        self.assertTrue((self.out/'card_index.json').is_file())
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                g.run(['--source',str(self.root),'--output',str(self.out)])
        with contextlib.redirect_stdout(io.StringIO()):
            code2=g.run(['--source',str(self.root),'--output',str(self.out),'--replace-output'])
        self.assertEqual(code2,0)

    def test_missing_chapter_and_checkpoint_are_explicit_inventory_failures(self):
        self.make_inventory()
        (self.root/'ch01'/'CPM eBooks - CC Geometry Lesson 1.1.5.html').unlink()
        (self.root/'checkpoints'/'7.html').unlink()
        inv=g.inventory(self.root)
        self.assertIn('ch01/lesson 1.1.5',inv['errors'])
        self.assertIn('7',inv['missing_checkpoints'])


if __name__=='__main__':
    unittest.main(verbosity=2)
