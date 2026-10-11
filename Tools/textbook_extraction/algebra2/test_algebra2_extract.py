#!/usr/bin/env python3
"""Algebra 2 canonical extraction tests. All fixtures generated locally, no licensed textbook content."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import algebra2_extract as a


def page(content):
    return '<!doctype html><html lang="en"><body><div id="contents">' + content + '</div></body></html>'


def question(pid, body):
    return ('<div class="contentContainerReference problem" id="' + pid + '" container-id="native-cpm">'
            '<div class="contentContainerReference-title">' + pid + '</div>'
            '<div class="contentContainerReference-body">' + body + '</div></div>')


class Algebra2ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.source = Path(self.temporary.name) / 'source'
        self.source.mkdir()
        self.output = Path(self.temporary.name) / 'private-output'
        self.qa = {'errors': [], 'warnings': []}

    def tearDown(self):
        self.temporary.cleanup()

    def add(self, folder, name, html):
        p = self.source / folder / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding='utf-8')
        return p

    def extract(self, p):
        self.output.mkdir(exist_ok=True)
        return a.extract_page(p, self.source, self.output, set(), {}, self.qa)

    def test_inventory_totals_and_appendix_mapping(self):
        self.assertEqual(sum(len(x.split()) for x in a.LESSONS.values()), 123)
        self.assertEqual(len(a.UNIT_DIRS), 15)
        self.assertEqual(len(a.EXPECTED_CHECKPOINTS), 18)
        self.assertEqual(a.UNIT_DIRS[13], 'appendixa')
        self.assertEqual(a.UNIT_DIRS[15], 'appendixc')
        self.assertEqual(a.source_role(Path('appendixc/CPM eBooks - CC Algebra 2 Lesson 15.closure.html')), ('closure','15'))
        self.assertEqual(a.source_role(Path('appendixa/CPM eBooks - CC Algebra 2 Lesson 13.1.1.html')), ('lesson','13.1.1'))
        self.assertEqual(a.source_role(Path('checkpoints/2a.html')), ('checkpoint','2a'))
        self.assertEqual(a.source_role(Path('standards/overview.html'))[0], 'standards')

    def test_numbered_lesson_source_math_and_media(self):
        images = self.source / 'ch01' / 'CPM eBooks - CC Algebra 2 Lesson 1.1.1_files'
        images.mkdir(parents=True)
        (images/'graph.png').write_bytes(b'fake graph')
        p=self.add('ch01','CPM eBooks - CC Algebra 2 Lesson 1.1.1.html',page(question('1-1',
            '<p>Plot this function: <c3po-media><script type="math/tex">\\sqrt{x}</script></c3po-media></p>'
            '<img src="./CPM eBooks - CC Algebra 2 Lesson 1.1.1_files/graph.png">')))
        card=next(c for c in self.extract(p) if c['card_type']=='problem')
        self.assertEqual(card['source_problem_id'],'1-1')
        self.assertEqual(card['chapter'],1)
        self.assertEqual(card['unit_kind'],'chapter')
        self.assertIn('assets/ch01',card['html'])
        self.assertIn(r'\sqrt{x}',card['math_tex'])
        self.assertEqual(card['media'][0]['status'],'copied')
        self.assertFalse(card['teacher_approved'])
        self.assertEqual(card['source_container_id'],'native-cpm')
        self.assertEqual(len(card['source_sha256']),64)

    def test_closure_keys_and_final_student_reflection(self):
        p=self.add('ch08','CPM eBooks - CC Algebra 2 Lesson 8.closure.html',page(
            question('CL 8-178','<p>Find roots.</p>')
            +question('CL 8-179','<p>Check your answers using the table. Which problems do you feel confident about? Which problems were hard?</p>')
            +'<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            +question('CL 8-178','<p>Solution: two roots.</p>')))
        cards=self.extract(p)
        sols=[c for c in cards if c['card_type']=='solution']
        self.assertEqual(len(sols),1)
        self.assertEqual(sols[0]['visibility'],'teacher_only')
        self.assertTrue(sols[0]['paired_student_card_id'])
        self.assertTrue(any(c['suggested_instructional_role']=='closure_self_assessment' for c in cards))
        self.assertFalse(any(x['warning']=='closure_question_without_key' for x in self.qa['warnings']))

    def test_chapter7_question_lacks_cl_prefix_in_source_but_paired(self):
        p=self.add('ch07','CPM eBooks - CC Algebra 2 Lesson 7.closure.html',page(
            question('7-167','Source question without the CL prefix.')
            +'<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            +question('CL 7-167','Source key includes the CL prefix.')))
        cards=self.extract(p)
        q=next(x for x in cards if x['card_type']=='problem')
        k=next(x for x in cards if x['card_type']=='solution')
        self.assertEqual(q['source_problem_id'],'7-167')
        self.assertEqual(k['source_problem_id'],'CL 7-167')
        self.assertEqual(q['paired_teacher_key_card_id'],k['card_id'])
        self.assertFalse(any(w['warning'] in ('unmatched_or_ambiguous_teacher_key','closure_question_without_key') for w in self.qa['warnings']))

    def test_nested_closure_questions_and_keys(self):
        p=self.add('ch03','CPM eBooks - CC Algebra 2 Lesson 3.closure.html',page('<ul><li>'
            +question('CL 3-100','Original question')
            +'<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            +question('CL 3-100','Solution: 9')+'</li></ul>'))
        cards=self.extract(p)
        self.assertEqual(len([x for x in cards if x['card_type']=='problem']),1)
        self.assertEqual(len([x for x in cards if x['card_type']=='solution']),1)
        self.assertEqual(len([x for x in cards if x['paired_teacher_key_card_id']]),1)

    def test_appendix_c_inconsistent_source_id_spacing_paired_without_relabel(self):
        p=self.add('appendixc','CPM eBooks - CC Algebra 2 Lesson 15.closure.html',page(
            question('CLC-62','<p>Original Appendix C problem.</p>')
            +'<h3>Answers and Support for Closure Activity #4 What Have I Learned?</h3>'
            +question('CL C-62','<p>Solution for appendix problem.</p>')))
        cards=self.extract(p)
        q=next(x for x in cards if x['card_type']=='problem')
        k=next(x for x in cards if x['card_type']=='solution')
        self.assertEqual(q['source_problem_id'],'CLC-62')
        self.assertEqual(k['source_problem_id'],'CL C-62')
        self.assertEqual(q['paired_teacher_key_card_id'],k['card_id'])
        self.assertEqual(k['paired_student_card_id'],q['card_id'])
        self.assertEqual(q['chapter'],15)
        self.assertEqual(q['unit_name'],'Appendix C')
        self.assertEqual(q['unit_kind'],'appendix')
        self.assertFalse(any(w['warning'] in ('unusual_problem_id','unmatched_or_ambiguous_teacher_key') for w in self.qa['warnings']))

    def test_checkpoint_practice_and_teacher_only_answers(self):
        assets=self.source/'checkpoints'/'2a_files';assets.mkdir(parents=True)
        (assets/'diagram.png').write_bytes(b'fake diagram')
        p=self.add('checkpoints','2a.html',page(
            '<h2>Checkpoint 2A</h2><p>Answers to problem 2-53: 17</p>'
            '<p>Example 1: Sample step</p>'
            '<p>Now we can go back and solve the original problems.</p>'
            '<p>Worked answer to the original question</p>'
            '<p>Here are some more to try.</p><ol><li>First practice</li>'
            '<li><img src="./2a_files/diagram.png"></li></ol>'
            '<p>Answers:</p><p>17 and 21</p>'))
        cards=self.extract(p)
        pr=[c for c in cards if c['suggested_instructional_role']=='checkpoint_practice']
        self.assertEqual(len(pr),2)
        self.assertEqual([c['source_list_item_number'] for c in pr],[1,2])
        self.assertTrue(all(c['visibility']=='student_candidate' for c in pr))
        self.assertTrue(all(c['source_problem_id'] is None for c in pr))
        self.assertEqual(pr[1]['media'][0]['status'],'copied')
        self.assertTrue(any(c['visibility']=='teacher_only' and 'Worked answer' in c['text'] for c in cards))
        self.assertTrue(any(c['visibility']=='teacher_only' and '17 and 21' in c['text'] for c in cards))

    def test_teacher_notes_and_outside_media(self):
        p=self.add('appendixb','CPM eBooks - CC Algebra 2 Teacher Notes 14.closure.html',page('<p>Teacher-only instruction.</p>'))
        self.assertTrue(all(c['visibility']=='teacher_only' for c in self.extract(p)))
        v=self.add('ch01','CPM eBooks - CC Algebra 2 Lesson 1.1.1.html',page(question('1-1','<img src="./missing.png"><img src="../../escape.png">')))
        c=next(x for x in self.extract(v) if x['card_type']=='problem')
        self.assertEqual([x['status'] for x in c['media']], ['missing_local_file','unsafe_outside_source'])

    def synthetic_inventory(self):
        for unit, lessons in a.LESSONS.items():
            folder=a.UNIT_DIRS[unit]
            for lesson in lessons.split():
                self.add(folder, f'CPM eBooks - CC Algebra 2 Lesson {lesson}.html',page(question(f'{unit}-1','Practice.')))
            for part in ('opening','closure'):
                self.add(folder,f'CPM eBooks - CC Algebra 2 Lesson {unit}.{part}.html',page('<p>Student section.</p>'))
                self.add(folder,f'CPM eBooks - CC Algebra 2 Teacher Notes {unit}.{part}.html',page('<p>Teacher section.</p>'))
            label=str(unit) if unit<=12 else 'ABC'[unit-13]
            (self.source/folder/f'CCA2 Ch {label} RPs.pdf').write_bytes(b'%PDF synthetic')
            parents=self.source/'parent_guides';parents.mkdir(exist_ok=True)
            suffix=' (1)' if unit<=12 else '_1'
            (parents/f'CCA2_PG_ch{label}{suffix}.pdf').write_bytes(b'%PDF synthetic')
        (self.source/'parent_guides'/'PG_intro_generic.pdf').write_bytes(b'%PDF synthetic')
        for n in a.EXPECTED_CHECKPOINTS:
            self.add('checkpoints',f'{n}.html',page('<p>Checkpoint material.</p>'))
        self.add('checkpoints','CPM eBooks - CC Algebra 2 Checkpoints.html',page('<p>Checkpoint index.</p>'))
        for n in ['1.html','2.html','3.html','4.html','5.html','overview.html','CPM eBooks - CC Algebra 2 Standards.html']:
            self.add('standards',n,page('<p>Standards material.</p>'))
        for n in range(7):
            (self.source/'standards'/f'standards_{n}.pdf').write_bytes(b'%PDF synthetic')
        self.add('', 'CPM eBooks - CC Algebra 2 Overview.html',page('<p>Course overview.</p>'))
        self.add('', 'CPM eBooks - CC Algebra 2 Table of Contents.html',page('<p>Full course structure.</p>'))
        (self.source/'misc').mkdir(exist_ok=True)
        for p in a.pages(self.source):
            p.with_name(p.stem + '_files').mkdir(exist_ok=True)

    def test_full_source_inventory_and_offline_local_execution(self):
        self.synthetic_inventory()
        inv=a.inventory(self.source)
        self.assertFalse(inv['errors'],inv['errors'])
        self.assertFalse(inv['missing_parent_guides'],inv['missing_parent_guides'])
        self.assertFalse(inv['missing_checkpoints'],inv['missing_checkpoints'])
        self.assertEqual(len(list(a.pages(self.source))), 211)
        self.assertEqual(len(a.resources(self.source)),38)
        with contextlib.redirect_stdout(io.StringIO()):
            exitcode=a.run(['--source',str(self.source),'--output',str(self.output)])
        self.assertEqual(exitcode,0)
        report=json.loads((self.output/'qa_report.json').read_text())
        self.assertEqual(report['summary']['numbered_lessons_found'],123)
        self.assertEqual(report['summary']['source_pages'],211)
        self.assertEqual(report['summary']['indexed_reference_pdfs'],38)
        self.assertEqual(report['summary']['missing_media'],0)
        self.assertTrue((self.output/'ALGEBRA2_GENERATED_OUTPUT.marker').is_file())
        self.assertTrue((self.output/'cards.jsonl').is_file())
        self.assertTrue((self.output/'resource_index.json').is_file())
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                a.run(['--source',str(self.source),'--output',str(self.output)])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.run(['--source',str(self.source),'--output',str(self.output),'--replace-output']),0)

    def test_missing_closure_or_appendix_or_checkpoint_is_inventory_error(self):
        self.synthetic_inventory()
        (self.source/'ch08'/'CPM eBooks - CC Algebra 2 Lesson 8.closure.html').unlink()
        (self.source/'appendixc'/'CPM eBooks - CC Algebra 2 Lesson 15.1.3.html').unlink()
        (self.source/'checkpoints'/'7a.html').unlink()
        inv=a.inventory(self.source)
        self.assertIn('ch08/student_closure',inv['errors'])
        self.assertIn('appendixc/lesson 15.1.3',inv['errors'])
        self.assertIn('7a',inv['missing_checkpoints'])

if __name__=='__main__':
    unittest.main(verbosity=2)
