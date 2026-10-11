#!/usr/bin/env python3
"""Precalculus private canonical extraction tests; all fixtures synthetic, no CPM source."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import precalculus_extract as a


def page(content):
    return '<!doctype html><html lang="en"><body><div id="contents">' + content + '</div></body></html>'


def problem(pid, content):
    return (f'<div class="contentContainerReference problem" id="{pid}" container-id="source-section">'
            f'<div class="contentContainerReference-title">{pid}</div>'
            f'<div class="contentContainerReference-body">{content}</div></div>')


class PrecalculusExtractionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = Path(self.tmp.name) / 'source'
        self.source.mkdir()
        self.out = Path(self.tmp.name) / 'private-output'
        self.qa = {'errors': [], 'warnings': []}

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, folder, filename, content):
        p = self.source / folder / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return p

    def extract(self, p):
        self.out.mkdir(exist_ok=True)
        return a.extract_page(p, self.source, self.out, set(), {}, self.qa)

    def test_complete_edition_skeleton(self):
        self.assertEqual(sum(len(x.split()) for x in a.LESSONS.values()), 121)
        self.assertEqual(len(a.UNIT_DIRS), 13)
        self.assertEqual(len(a.EXPECTED_CHECKPOINTS), 17)
        self.assertIn('13.2.2A', a.LESSONS[13].split())
        self.assertEqual(a.source_role(Path('ch13/CPM eBooks - Precalculus Third Edition Lesson 13.2.2A.html')), ('lesson', '13.2.2A'))
        self.assertEqual(a.source_role(Path('ch13/CPM eBooks - Precalculus Third Edition Teacher Notes 13.closure.html')), ('teacher_closure', '13'))
        self.assertEqual(a.source_role(Path('checkpoints/12a.html')), ('checkpoint', '12a'))
        self.assertEqual(a.source_role(Path('checkpoints/6.html')), ('checkpoint', '6'))
        self.assertEqual(a.source_role(Path('checkpoints/6b.html')), ('checkpoint', '6b'))

    def test_lesson_13_2_2A_keeps_original_name_and_math_media(self):
        media=self.source/'ch13'/'CPM eBooks - Precalculus Third Edition Lesson 13.2.2A_files'
        media.mkdir(parents=True)
        (media/'polar.png').write_bytes(b'synthetic image')
        p=self.add('ch13','CPM eBooks - Precalculus Third Edition Lesson 13.2.2A.html',page(problem('13-99',
            '<p>Represent a point: <c3po-media><script type="math/tex">r=2\\sin\\theta</script></c3po-media></p>'
            '<img src="./CPM eBooks - Precalculus Third Edition Lesson 13.2.2A_files/polar.png">')))
        card=next(c for c in self.extract(p) if c['card_type']=='problem')
        self.assertEqual(card['lesson_id'],'13.2.2A')
        self.assertEqual(card['unit_kind'],'chapter')
        self.assertEqual(card['course'],'precalculus')
        self.assertEqual(card['media'][0]['status'],'copied')
        self.assertIn('assets/ch13',card['html'])
        self.assertIn(r'r=2\sin\theta',card['math_tex'])
        self.assertEqual(len(card['source_sha256']),64)
        self.assertFalse(card['teacher_approved'])

    def test_closure_self_reflection_chapter1_wording(self):
        p=self.add('ch01',f'{a.SOURCE_PREFIX} Lesson 1.closure.html',page(
            problem('CL 1-140','Solve problem.')
            + problem('CL 1-149','Check your answers in the following table. Which problems made you think?')
            + '<h3>Answers and Support for Closure</h3>'
            + problem('CL 1-140','Solution: answer.')))
        cs=self.extract(p)
        self.assertEqual(sum(c['card_type']=='solution' for c in cs),1)
        self.assertEqual(sum(c['suggested_instructional_role']=='closure_self_assessment' for c in cs),1)
        self.assertFalse([w for w in self.qa['warnings'] if w['warning'] in ('closure_question_without_key','unmatched_or_ambiguous_teacher_key')])

    def test_closure_self_reflection_chapter2_wording(self):
        p=self.add('ch02',f'{a.SOURCE_PREFIX} Lesson 2.closure.html',page(
            problem('CL 2-161','Solve.')
            + problem('CL 2-172','Check your answers using the following table. Which problems made you think?')
            + '<h3>Answers and Support for Closure</h3>'
            + problem('CL 2-161','Solution: answer.')))
        cs=self.extract(p)
        self.assertEqual(sum(c['suggested_instructional_role']=='closure_self_assessment' for c in cs),1)
        self.assertFalse(any(w['warning']=='closure_question_without_key' for w in self.qa['warnings']))

    def test_preserve_space_in_source_problem_id(self):
        p=self.add('ch06',f'{a.SOURCE_PREFIX} Lesson 6.closure.html',page(
            problem('CL 6-143 ','Source label with a trailing space.')
            + '<h3>Answers and Support for Closure</h3>'
            + problem('CL 6-143','Solution.')))
        cs=self.extract(p)
        student=next(c for c in cs if c['card_type']=='problem')
        sol=next(c for c in cs if c['card_type']=='solution')
        self.assertEqual(student['source_problem_id'],'CL 6-143 ')
        self.assertEqual(student['paired_teacher_key_card_id'],sol['card_id'])
        self.assertFalse(any(w['warning'] in ('unusual_problem_id','unmatched_or_ambiguous_teacher_key') for w in self.qa['warnings']))

    def test_nested_closure_question_key_with_teacher_visibility(self):
        p=self.add('ch08',f'{a.SOURCE_PREFIX} Lesson 8.closure.html',page(
            '<ul><li>' + problem('CL 8-201','Question') + '<h3>Answers and Support for Closure</h3>'
            + problem('CL 8-201','Solution') + '</li></ul>'))
        cs=self.extract(p)
        student=next(c for c in cs if c['card_type']=='problem')
        sol=next(c for c in cs if c['card_type']=='solution')
        self.assertEqual(student['paired_teacher_key_card_id'],sol['card_id'])
        self.assertEqual(sol['visibility'],'teacher_only')
        self.assertEqual(sum(c['card_type']=='solution' for c in cs),1)

    def test_checkpoint_diagram_list_items_and_answers(self):
        media=self.source/'checkpoints'/'12a_files';media.mkdir(parents=True)
        (media/'conic.png').write_bytes(b'synthetic png')
        p=self.add('checkpoints','12a.html',page(
            '<p>Example 1: A worked example.</p>'
            '<h3>Here are some more to try.</h3><ol><li>First</li>'
            '<li><img src="./12a_files/conic.png"></li></ol>'
            '<h3>Answers:</h3><p>Sample answers</p>'))
        cs=self.extract(p)
        pr=[c for c in cs if c['suggested_instructional_role']=='checkpoint_practice']
        self.assertEqual(len(pr),2)
        self.assertEqual([c['source_list_item_number'] for c in pr],[1,2])
        self.assertTrue(all(c['visibility']=='student_candidate' for c in pr))
        self.assertEqual(pr[1]['media'][0]['status'],'copied')
        self.assertTrue(any(c['visibility']=='teacher_only' and 'Sample answers' in c['text'] for c in cs))

    def test_teacher_notes_and_guard_missing_unsafe_assets(self):
        p=self.add('ch13',f'{a.SOURCE_PREFIX} Teacher Notes 13.closure.html',page('<p>Only for the teacher.</p>'))
        self.assertTrue(all(c['visibility']=='teacher_only' for c in self.extract(p)))
        p=self.add('ch01',f'{a.SOURCE_PREFIX} Lesson 1.1.1.html',page(problem('1-1','<img src="./missing.png"><img src="../../escape.png">')))
        card=next(c for c in self.extract(p) if c['card_type']=='problem')
        self.assertEqual([m['status'] for m in card['media']],['missing_local_file','unsafe_outside_source'])

    def synthetic_source(self):
        for n,lessons in a.LESSONS.items():
            chapter=f'ch{n:02d}'
            for lesson in lessons.split():
                self.add(chapter,f'{a.SOURCE_PREFIX} Lesson {lesson}.html',page(problem(f'{n}-1','A practice problem.')))
            for part in ('opening','closure'):
                self.add(chapter,f'{a.SOURCE_PREFIX} Lesson {n}.{part}.html',page('<p>Student text.</p>'))
                self.add(chapter,f'{a.SOURCE_PREFIX} Teacher Notes {n}.{part}.html',page('<p>Teacher text.</p>'))
            (self.source/chapter/f'pc3_ch{n}_rps.pdf').write_bytes(b'%PDF synthetic')
        self.add('', f'{a.SOURCE_PREFIX} Table of Contents.html',page('<p>TOC.</p>'))
        self.add('', f'{a.SOURCE_PREFIX} Overview.html',page('<p>Overview.</p>'))
        for cp in a.EXPECTED_CHECKPOINTS:
            self.add('checkpoints',f'{cp}.html',page('<p>Checkpoint material.</p>'))
        self.add('checkpoints',f'{a.SOURCE_PREFIX} Checkpoints.html',page('<p>Checkpoint index.</p>'))
        (self.source/'standards').mkdir()
        for name in a.EXPECTED_STANDARDS_PDFS:
            (self.source/'standards'/name).write_bytes(b'%PDF synthetic')
        (self.source/'misc').mkdir()
        for name in ('pc3_rps.pdf','PC Skill Builders.pdf'):
            (self.source/'misc'/name).write_bytes(b'%PDF synthetic')
        (self.source/'parent_guides').mkdir()
        for p in a.pages(self.source):
            p.with_name(p.stem+'_files').mkdir(exist_ok=True)

    def test_full_inventory_and_private_run(self):
        self.synthetic_source()
        inv=a.inventory(self.source)
        self.assertEqual(inv['errors'],[])
        self.assertEqual(inv['missing_parent_guides'],[])
        self.assertEqual(inv['missing_checkpoints'],[])
        self.assertEqual(len(list(a.pages(self.source))),193)
        self.assertEqual(len(a.resources(self.source)),19)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.run(['--source',str(self.source),'--output',str(self.out)]),0)
        qa=json.loads((self.out/'qa_report.json').read_text())
        self.assertEqual(qa['summary']['numbered_lessons_found'],121)
        self.assertEqual(qa['summary']['source_pages'],193)
        self.assertEqual(qa['summary']['indexed_reference_pdfs'],19)
        self.assertEqual(qa['summary']['missing_media'],0)
        self.assertTrue((self.out/'PRECALCULUS_GENERATED_OUTPUT.marker').exists())
        self.assertTrue((self.out/'cards.jsonl').is_file())
        self.assertTrue((self.out/'resource_index.json').is_file())
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                a.run(['--source',str(self.source),'--output',str(self.out)])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.run(['--source',str(self.source),'--output',str(self.out),'--replace-output']),0)

    def test_inventory_detects_missing_chapter_13_and_checkpoint12a(self):
        self.synthetic_source()
        (self.source/'ch13'/f'{a.SOURCE_PREFIX} Lesson 13.2.2A.html').unlink()
        (self.source/'ch06'/f'{a.SOURCE_PREFIX} Lesson 6.closure.html').unlink()
        (self.source/'checkpoints'/'12a.html').unlink()
        inv=a.inventory(self.source)
        self.assertIn('ch13/lesson 13.2.2A',inv['errors'])
        self.assertIn('ch06/student_closure',inv['errors'])
        self.assertIn('12a',inv['missing_checkpoints'])

    def test_other_inadequate_output_is_protected(self):
        self.synthetic_source()
        self.out.mkdir()
        (self.out/'keep.txt').write_text('Do not delete')
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                a.run(['--source',str(self.source),'--output',str(self.out),'--replace-output'])
        self.assertTrue((self.out/'keep.txt').exists())

if __name__=='__main__':
    unittest.main(verbosity=2)
