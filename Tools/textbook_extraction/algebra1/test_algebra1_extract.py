"""Regression tests for private Core Connections Algebra canonical card extractor."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from algebra1_extract import LESSONS,EXPECTED_LESSON_TOTAL,EXPECTED_CHECKPOINTS,source_name,extract_page,main,DOM,render_content,find_first

class AlgebraExtractorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.src=Path(self.tmp.name)/'cc_algebra';self.src.mkdir()
        self.dst=Path(self.tmp.name)/'generated'
        self.dst.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def simple(self,dir,name,content=None):
        d=self.src/dir;d.mkdir(exist_ok=True)
        html=content or '<html><div id="contents"><header class="lessonTitle"><h1>Example</h1></header><p>Original CPM exposition</p><div class="contentContainerReference problem" id="1-1" container-id="abc"><div class="contentContainerReference-title">1-1.</div><div class="contentContainerReference-body">Original question</div></div></div></html>'
        f=d/name;f.write_text(html,encoding='utf-8'); (d/f'{f.stem}_files').mkdir(exist_ok=True)
        return f
    def test_short_chapter_1_filename(self):
        p=self.simple('ch01','1-1-1.html')
        self.assertEqual(('lesson','1.1.1'),source_name(p))
        self.assertEqual(('opening','1'),source_name(self.simple('ch01','intro.html')))
        self.assertEqual(('closure','1'),source_name(self.simple('ch01','closure.html')))
        qa={'errors':[],'warnings':[]}
        cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual('1.1.1',cards[0]['lesson_id'])
        self.assertEqual('algebra1:ch01_lesson_1_1_1:exposition_001',cards[0]['card_id'])
    def test_extension_and_misspelled_opening(self):
        p=self.simple('ch02','extraactivity.html')
        self.assertEqual(('lesson','2.4.1'),source_name(p))
        self.assertEqual(('opening','2'),source_name(self.simple('ch02','intr0.html')))
    def test_appendix_a_numbered_and_teacher_notes(self):
        p=self.simple('appendix_a','CPM eBooks - CC Algebra Lesson 12.1.9.html')
        qa={'errors':[],'warnings':[]}; cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual(12,cards[0]['chapter'])
        self.assertEqual('12.1.9',cards[0]['lesson_id'])
        self.assertEqual('teacher_opening',source_name(self.simple('appendix_a','CPM eBooks - CC Algebra Teacher Notes 12.opening.html'))[0])
    def test_solution_question_and_teacher_visibility(self):
        html='''<div id="contents"><p>Closure</p>
<div class="contentContainerReference problem" id="CL 1-85"><div class="contentContainerReference-body"><p>Question 85</p></div></div>
<div class="contentContainerReference problem" id="CL1-85"><div class="contentContainerReference-body"><p>Solution&nbsp; 12</p></div></div></div>'''
        p=self.simple('ch01','closure.html',html)
        qa={'errors':[],'warnings':[]};cards=extract_page(p,self.src,self.dst,set(),qa)
        st=[z for z in cards if z['card_type']=='problem'];key=[z for z in cards if z['card_type']=='solution']
        self.assertEqual((1,1),(len(st),len(key)))
        self.assertEqual([],qa['warnings'])
        self.assertEqual('teacher_only',key[0]['visibility'])
        self.assertEqual(key[0]['card_id'],st[0]['paired_teacher_key_card_id'])
        self.assertEqual(st[0]['card_id'],key[0]['paired_student_card_id'])
    def test_9_47_solutions_to_is_a_student_question(self):
        p=self.simple('ch09','CPM eBooks - CC Algebra Lesson 9.2.1.html', 
          '<div id="contents"><div class="contentContainerReference problem" id="9-47">'
          '<div class="contentContainerReference-body"><p>SOLUTIONS TO A LINEAR INEQUALITY</p>'
          '<p>With your study team, find at least five solutions.</p></div></div></div>')
        qa={'errors':[],'warnings':[]};cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual([],qa['warnings'])
        self.assertEqual(1,len(cards))
        self.assertEqual('problem',cards[0]['card_type'])
        self.assertEqual('student_candidate',cards[0]['visibility'])
        self.assertIsNone(cards[0]['paired_student_card_id'])
    def test_appendix_a_ids_are_canonical(self):
        p=self.simple('appendix_a','CPM eBooks - CC Algebra Lesson 12.1.1.html',
          '<div id="contents"><div class="contentContainerReference problem" id="A-1">'
          '<div class="contentContainerReference-body"><p>Use algebra tiles.</p></div></div>'
          '<div class="contentContainerReference problem" id="A-2">'
          '<div class="contentContainerReference-body"><p>Draw the tiles.</p></div></div></div>')
        qa={'errors':[],'warnings':[]};cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual([],qa['warnings'])
        self.assertEqual(['A-1','A-2'],[c['source_problem_id'] for c in cards])
    def test_appendix_a_closure_more_solution_is_teacher_only(self):
        p=self.simple('appendix_a','CPM eBooks - CC Algebra Lesson 12.closure.html',
          '<div id="contents"><div class="contentContainerReference problem" id="CL A-98">'
          '<div class="contentContainerReference-body"><p>Examine the Expression Mat.</p></div></div>'
          '<div class="contentContainerReference problem" id="CL A-98">'
          '<div class="contentContainerReference-body"><p>More Solution &nbsp; x = 2.</p></div></div>'
          '<div class="contentContainerReference problem" id="CL A-99">'
          '<div class="contentContainerReference-body"><p>Find the equivalent fraction.</p></div></div>'
          '<div class="contentContainerReference problem" id="CL A-99">'
          '<div class="contentContainerReference-body"><p>Solution &nbsp; one half.</p></div></div></div>')
        qa={'errors':[],'warnings':[]};cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual([],qa['warnings'])
        self.assertEqual(4,len(cards))
        self.assertEqual(2,sum(c['card_type']=='solution' for c in cards))
        for key in [c for c in cards if c['card_type']=='solution']:
            self.assertEqual('teacher_only',key['visibility'])
            self.assertTrue(key['paired_student_card_id'])
            question=next(c for c in cards if c['card_id']==key['paired_student_card_id'])
            self.assertEqual(key['card_id'],question['paired_teacher_key_card_id'])

    def test_image_math_and_external_links(self):
        p=self.simple('ch03','CPM eBooks - CC Algebra Lesson 3.1.1.html', '''<div id="contents">
<div class="contentContainerReference problem" id="3-5"><div class="contentContainerReference-body"><p>Check the tiles</p><img src="./CPM eBooks - CC Algebra Lesson 3.1.1_files/tile.png"><c3po-media><span class="MathJax_SVG">SVG snapshot</span><script type="math/tex">x^2=9</script></c3po-media><a href="https://technology.cpm.org/example">eTool</a></div></div>
</div>''')
        (p.parent/(p.stem+'_files')/'tile.png').write_bytes(b'\x89PNG\r\n')
        qa={'errors':[],'warnings':[]};cards=extract_page(p,self.src,self.dst,set(),qa)
        self.assertEqual([],qa['warnings'])
        self.assertEqual('copied',cards[0]['media'][0]['status'])
        self.assertEqual(['x^2=9'],cards[0]['math_tex'])
        self.assertIn('data-tex="x^2=9"',cards[0]['html'])
        self.assertEqual('https://technology.cpm.org/example',cards[0]['external_links'][0]['url'])
    def test_security_filtering(self):
        d=DOM();d.feed('<div id="contents"><p onclick="evil()">safe</p><script>alert(1)</script><img src="javascript:evil()" onerror="bad()"></div>')
        frag=render_content(find_first(d.root,lambda n:n.attr('id')=='contents'))
        for bad in ['evil()', 'alert(1)', 'onerror']:
            self.assertNotIn(bad,frag)
    def test_course_toc_count(self):
        self.assertEqual(112,sum(len(x.split()) for x in LESSONS.values()))
        self.assertEqual(112,EXPECTED_LESSON_TOTAL)
        self.assertEqual(15,len(EXPECTED_CHECKPOINTS))

if __name__=='__main__':unittest.main()
