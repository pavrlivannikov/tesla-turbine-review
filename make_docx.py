#!/usr/bin/env python3
"""Конвертирует .md в .docx — простая версия без парсинга md, напрямую."""
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
import re, os

BASE = '/home/paveladmin/.openclaw/workspace/projects/vsyako-razno'

JOBS = [
    ('final-article.md', 'final-article.docx', 'Турбина Теслы: от патента до современных рабочих тел'),
    ('PROJECT.md', 'PROJECT.docx', 'Проект: Турбина Теслы — итоговый документ'),
    ('obzor-turbina-tesla.md', 'obzor-turbina-tesla.docx', 'Турбина Теслы — обзор'),
]

def add_header_footer(doc, title_text):
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)
        header = section.header
        h = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        h.text = title_text
        h.style.font.size = Pt(10)
        for run in h.runs:
            run.font.size = Pt(10)
            run.font.name = 'Times New Roman'
        footer = section.footer
        f = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f.add_run('Страница ')
        # page number field
        fld = f.add_run()
        fld_char = doc.element.makeelement(qn('w:fldChar'), {qn('w:fldCharType'): 'begin'})
        instr = doc.element.makeelement(qn('w:instrText'), {})
        instr.text = ' PAGE '
        fld2 = doc.element.makeelement(qn('w:fldChar'), {qn('w:fldCharType'): 'end'})
        run1 = f.add_run()
        run1._r.append(fld_char)
        f.add_run('1')._r.append(instr)
        run2 = f.add_run()
        run2._r.append(fld2)

def set_font(run, name='Times New Roman', size=14):
    run.font.name = name
    run.font.size = Pt(size)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = doc.element.makeelement(qn('w:rFonts'), {})
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)

def add_paragraph(doc, text, size=14, bold=False, align=None, font_name='Times New Roman'):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    fmt = p.paragraph_format
    fmt.space_after = Pt(6)
    fmt.line_spacing = 1.15
    run = p.add_run(text)
    set_font(run, font_name, size)
    run.bold = bold
    return p

def add_code_para(doc, text):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.space_after = Pt(4)
    fmt.line_spacing = 1.0
    run = p.add_run(text)
    set_font(run, 'Courier New', 11)
    return p

def add_table(doc, rows):
    """rows: list of lists, first row = header"""
    if not rows:
        return
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = 'Table Grid'
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            run = p.add_run(str(cell_text))
            size = 11 if i > 0 else 11
            set_font(run, 'Times New Roman', size)
            run.bold = (i == 0)
            if i == 0:
                # header shading
                shading = cell._tc.get_or_add_tcPr()
                shd = doc.element.makeelement(qn('w:shd'), {
                    qn('w:fill'): 'D9D9D9',
                    qn('w:val'): 'clear'
                })
                shading.append(shd)
    doc.add_paragraph()  # spacer

def convert_md_to_docx(md_path, docx_path, header_title):
    global doc
    doc = Document()
    add_header_footer(doc, header_title)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    in_table = False
    table_data = []
    in_code = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Title (first # heading)
        if line.startswith('# ') and i < 3:
            add_paragraph(doc, line[2:], size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
            doc.add_paragraph()
            i += 1
            continue
        
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                in_code = False
                for cl in code_lines:
                    add_code_para(doc, cl)
                code_lines = []
                doc.add_paragraph()
            else:
                in_code = True
            i += 1
            continue
        
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        
        # Headings
        if line.startswith('## '):
            add_paragraph(doc, line[3:], size=18, bold=True)
            i += 1
            continue
        if line.startswith('### '):
            add_paragraph(doc, line[4:], size=16, bold=True)
            i += 1
            continue
        if line.startswith('#### '):
            add_paragraph(doc, line[5:], size=14, bold=True)
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            doc.add_paragraph()
            i += 1
            continue
        
        # Table detection
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_data = []
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                i += 1
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            table_data.append(cells)
            i += 1
            # Check if next line is still a table
            if i < len(lines) and '|' not in lines[i]:
                in_table = False
                add_table(doc, table_data)
            continue
        elif in_table:
            in_table = False
            if table_data:
                add_table(doc, table_data)
        
        # Regular paragraph
        if line.strip():
            # Bold markers
            text = line.strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold markers stripped
            # But keep the content, handle italics too
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            add_paragraph(doc, text, size=14)
        else:
            doc.add_paragraph()
        
        i += 1
    
    # Flush remaining table
    if in_table and table_data:
        add_table(doc, table_data)
    
    doc.save(docx_path)
    return os.path.getsize(docx_path)

for md_name, docx_name, title in JOBS:
    md_path = os.path.join(BASE, md_name)
    docx_path = os.path.join(BASE, docx_name)
    size = convert_md_to_docx(md_path, docx_path, title)
    print(f"✅ {docx_name}: {size/1024:.0f} KB")

print("Готово: 3 DOCX")
