import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from cc1_extract import DOM, find_first, plain, render_content, source_name, extract_page, inventory, safe_slug, media_refs

class CC1ExtractorTests(unittest.TestCase):
 def setUp(self):
  self.td=TemporaryDirectory()
  self.root=Path(self.td.name)/'cc1';self.root.mkdir()
  self.out=Path(self.td.name)/'out';self.out.mkdir()
 def tearDown(self):self.td.cleanup()
 def fixture(self):
  lesson=self.root/'ch01';lesson.mkdir()
  name='CPM eBooks - CC Course 1 Lesson 1.1.2.html'
  assets=lesson/(name[:-5]+'_files');assets.mkdir()
  (assets/'tile.png').write_bytes(b'\x89PNG\r\n')
  p=lesson/name
  p.write_text('''<!DOCTYPE html>
<!-- saved from url=(0066)https://ebooks.cpm.org/bookdb.php?title=cc1&name=1.1.2&type=lesson -->
<div id="contents"><script>console.log('metadata')</script><div class="c3po-metadata"></div>
<header class="lessonTitle"><h1>1.1.2 How does it change?</h1><p>Perimeter and Area Relationships</p></header>
<p>Many ancient cities.</p><p><c3po-media><span class="MathJax_SVG"><svg><use href="#glyph"></use></svg></span><script type="math/tex" id="MathJax-Element-1">x+2=4</script></c3po-media></p>
<div class="contentContainerReference problem" id="1-5" container-id="abcdef"><div class="contentContainerReference-title">1-5.</div><div class="contentContainerReference-body"><p>Toothpicks and Tiles</p><p><img src="./CPM eBooks - CC Course 1 Lesson 1.1.2_files/tile.png" alt="square tiles"></p><a href="https://technology.cpm.org/general/tiles/">Student eTool</a></div></div>
<p><img src="./CPM eBooks - CC Course 1 Lesson 1.1.2_files/reviewpreview.png" alt="Review and Preview problems below"></p>
<div class="contentContainerReference problem" id="1-10" container-id="xyz"><div class="contentContainerReference-title">1-10.</div><p>Independent question</p></div>
</div>''',encoding='utf-8')
  return p
 def test_extract(self):
  page=self.fixture();qa={'errors':[],'warnings':[]};copied=set()
  cards=extract_page(page,self.root,self.out,copied,qa)
  self.assertEqual(4,len(cards))
  self.assertEqual(['exposition','problem','exposition','problem'],[x['card_type'] for x in cards])
  self.assertEqual('1-5',cards[1]['source_problem_id'])
  self.assertEqual('abcdef',cards[1]['source_container_id'])
  self.assertEqual('review_preview',cards[3]['suggested_instructional_role'])
  self.assertTrue(any(m['status']=='copied' for m in cards[1]['media']))
  self.assertTrue(any(m['status']=='missing_local_file' for m in cards[2]['media']))
  self.assertEqual('x+2=4',cards[0]['math_tex'][0])
  self.assertIn('data-tex="x+2=4"',cards[0]['html'])
  self.assertNotIn('MathJax_SVG',cards[0]['html'])
  self.assertTrue((self.out/'assets/ch01'/'CPM eBooks - CC Course 1 Lesson 1.1.2_files'/'tile.png').exists())
  self.assertTrue(qa['warnings']==[])
 def test_pip_title(self):
  d=self.root/'pip';d.mkdir();p=d/'7.html';p.write_text('<div id="contents"><ul><li><strong>PI-7. TEST</strong></li><li>A puzzle</li></ul></div>')
  qa={'errors':[],'warnings':[]}
  cards=extract_page(p,self.root,self.out,set(),qa)
  self.assertEqual(1,len(cards));self.assertEqual('puzzle_investigator',cards[0]['suggested_instructional_role'])
 def test_closed_world(self):
  self.fixture();qa={'errors':[],'warnings':[]}
  d=DOM();d.feed('<div id="contents">X<script>alert(1)</script><img onload="alert(1)" src="javascript:alert(2)"></div>')
  node=find_first(d.root,lambda n:n.attr('id')=='contents')
  frag=render_content(node)
  self.assertNotIn('alert(1)',frag)
  self.assertNotIn('onload',frag)
  self.assertNotIn('javascript:',frag)
if __name__=='__main__':unittest.main()
