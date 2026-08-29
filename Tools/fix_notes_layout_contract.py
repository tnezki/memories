#!/usr/bin/env python3
"""Repair legacy Notes markup to the deployed Notes CSS contracts."""
from pathlib import Path
import re, sys
TARGET=Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path(__file__).parent
VOCAB_SECTION_RE=re.compile(r'(<section\b[^>]*class=["\'][^"\']*\bvocab-preview-section\b[^"\']*["\'][^>]*>)(.*?)(</section>)',re.I|re.S)
SKIM_SECTION_RE=re.compile(r'(<section\b[^>]*class=["\'][^"\']*\bskim-section-task\b[^"\']*["\'][^>]*>)(.*?)(</section>)',re.I|re.S)
TR_RE=re.compile(r'<tr\b(?P<attrs>[^>]*)>(?P<body>.*?)</tr>',re.I|re.S)
ESCAPE_ONLY_RE=re.compile(r'>(?P<junk>\s*(?:(?:\\n|\\r|\\t)\s*)+)<',re.I)
SUSPICIOUS_ESCAPE_RE=re.compile(r'\\[nrt](?=\\|\s|<|$)')
TEACHER_STYLE='''<style id="teacher-notes-natural-flow">\n.notes-ws, .notes-task-workspace { height:auto !important; min-height:0 !important; overflow:visible !important; }\n.notes-task, .notes-task-content, .notes-discuss-task, .notes-ican-start { break-inside:auto !important; page-break-inside:auto !important; }\n@media print { .notes-ws, .notes-task-workspace { height:auto !important; min-height:0 !important; overflow:visible !important; } }\n</style>'''
def _replace_class_token(classes,old,new):
    out=[]
    for p in classes.split():
        p=new if p==old else p
        if p not in out: out.append(p)
    return ' '.join(out)
def _fix_vocab(match):
    opening,inner,closing=match.groups()
    def table_repl(m):
        classes=m.group(1)
        if 'vocab-sort-table' in classes.split() or 'vocab-sort' not in classes.split(): return m.group(0)
        return m.group(0).replace(classes,_replace_class_token(classes,'vocab-sort','vocab-sort-table'),1)
    inner=re.sub(r'<table\b[^>]*class=["\']([^"\']*)["\'][^>]*>',table_repl,inner,flags=re.I|re.S)
    def tr_repl(m):
        attrs,body=m.group('attrs'),m.group('body')
        if 'vocab-sort-space' not in attrs and 'vocab-sort-space' not in body:return m.group(0)
        def tdclass(cm):
            keep=[c for c in cm.group(1).split() if c!='vocab-sort-space']; return f'class="{" ".join(keep)}"' if keep else ''
        body=re.sub(r'class=["\']([^"\']*\bvocab-sort-space\b[^"\']*)["\']',tdclass,body,flags=re.I)
        if 'vocab-sort-space' not in attrs:
            cm=re.search(r'class=["\']([^"\']*)["\']',attrs,flags=re.I)
            if cm:
                new=(cm.group(1)+' vocab-sort-space').strip(); attrs=attrs[:cm.start()]+f'class="{new}"'+attrs[cm.end():]
            else: attrs+=' class="vocab-sort-space"'
        return f'<tr{attrs}>{body}</tr>'
    inner=TR_RE.sub(tr_repl,inner)
    inner=re.sub(r'<p\b([^>]*?)class=["\']vocab-note["\']([^>]*)>',r'<p\1class="vocab-sort-directions"\2>',inner,count=1,flags=re.I)
    if 'vocab-sort-table' in inner and 'vocab-sort-task' not in inner:
        d=re.search(r'<p\b[^>]*class=["\']vocab-sort-directions["\'][^>]*>.*?</p>',inner,re.I|re.S); t=re.search(r'<table\b[^>]*class=["\'][^"\']*\bvocab-sort-table\b[^"\']*["\'][^>]*>.*?</table>',inner,re.I|re.S)
        if d and t and d.start()<t.start(): inner=inner[:d.start()]+'<div class="vocab-sort-task">'+inner[d.start():t.end()]+'</div>'+inner[t.end():]
    return opening+inner+closing
def _fix_skim(match):
    opening,inner,closing=match.groups()
    if 'skim-section-directions' not in inner:
        inner=re.sub(r'(<h2\b[^>]*>.*?</h2>\s*)<p(?![^>]*class=)([^>]*)>',r'\1<p class="skim-section-directions"\2>',inner,count=1,flags=re.I|re.S)
    def table_repl(m):
        classes=m.group(1); parts=classes.split()
        if 'skim-section-table' in parts or 'preview-notes-table' not in parts:return m.group(0)
        return m.group(0).replace(classes,_replace_class_token(classes,'preview-notes-table','skim-section-table'),1)
    inner=re.sub(r'<table\b[^>]*class=["\']([^"\']*)["\'][^>]*>',table_repl,inner,flags=re.I|re.S)
    return opening+inner+closing
def fix_file(path):
    text=path.read_text(encoding='utf-8'); repaired=VOCAB_SECTION_RE.sub(_fix_vocab,text); repaired=SKIM_SECTION_RE.sub(_fix_skim,repaired); repaired=ESCAPE_ONLY_RE.sub('>\n<',repaired)
    if path.stem.lower().endswith('_teacher') and 'teacher-notes-natural-flow' not in repaired: repaired=re.sub(r'</head\s*>',TEACHER_STYLE+'\n</head>',repaired,count=1,flags=re.I)
    if repaired!=text: path.write_text(repaired,encoding='utf-8'); return True
    return False
def main():
    files=[TARGET] if TARGET.is_file() and TARGET.suffix.lower()=='.html' else sorted(TARGET.rglob('*.html')) if TARGET.is_dir() else []
    changed=[]; warnings=[]
    for p in files:
        if fix_file(p): changed.append(p)
        raw=p.read_text(encoding='utf-8'); visible=re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<[^>]+>',' ',raw,flags=re.I|re.S)
        if SUSPICIOUS_ESCAPE_RE.search(visible): warnings.append(p)
    print(f'Checked {len(files)} HTML file(s).'); print(f'Fixed {len(changed)} file(s).')
    for p in changed: print(f'  FIXED: {p}')
    if warnings:
        print('FAIL: suspicious visible escaped whitespace remains:')
        for p in warnings: print(f'  {p}')
        raise SystemExit(2)
    print('Visible escaped-whitespace audit: PASS')
if __name__=='__main__': main()
