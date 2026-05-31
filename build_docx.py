#!/usr/bin/env python3
"""Convert the Turbina Tesla markdown article to a styled DOCX document."""

import re
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

INPUT = "/home/paveladmin/.openclaw/workspace/projects/vsyako-razno/obzor-turbina-tesla.md"
OUTPUT = "/home/paveladmin/.openclaw/workspace/projects/vsyako-razno/obzor-turbina-tesla.docx"

# ── helpers ──────────────────────────────────────────────────────────────────

def set_cell_shading(cell, color):
    """Set background shading for a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_border(cell, **kwargs):
    """Set borders on a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge, val in kwargs.items():
        el = parse_xml(
            f'<w:{edge} {nsdecls("w")} w:val="{val.get("val", "single")}" '
            f'w:sz="{val.get("sz", "4")}" '
            f'w:color="{val.get("color", "000000")}" '
            f'w:space="0"/>'
        )
        tcBorders.append(el)
    tcPr.append(tcBorders)

def add_formula_block(doc, formula_text):
    """Add formula in Courier New, separate line."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(formula_text)
    run.font.name = "Courier New"
    run.font.size = Pt(10)
    run.bold = True
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)

def add_normal_text(doc, text):
    """Add paragraph with default body style."""
    p = doc.add_paragraph(text)
    style = p.style
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
    p.paragraph_format.line_spacing = 1.15
    return p

def add_bullet_list(doc, items):
    """Add bullet list items."""
    for item in items:
        p = doc.add_paragraph(item, style="List Bullet")
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        p.paragraph_format.line_spacing = 1.15

def is_markdown_table_line(line):
    """Check if a line is part of a markdown table."""
    stripped = line.strip()
    return (stripped.startswith("|") and stripped.endswith("|")) or (
        stripped.startswith("|") and "---" in stripped
    )

def is_markdown_hr(line):
    return line.strip().startswith("---") and "---" in line.strip()

def parse_table_rows(lines):
    """Parse markdown table lines into rows of cells."""
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        # skip alignment row (|---|---|)
        if re.match(r'^\|[\s\-:|]+\|$', stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows

def render_table(doc, rows):
    """Render parsed table into a Word table with styling."""
    if not rows:
        return
    num_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Enable all borders
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_text in enumerate(row_data):
            if col_idx >= num_cols:
                continue
            cell = table.cell(row_idx, col_idx)
            # Strip markdown formatting from alignment markers
            cell_text_clean = cell_text
            # Handle bold markers
            cell_text_clean = cell_text_clean.replace("**", "")
            # Handle markdown comment-style markers in tables
            cell.text = cell_text_clean

            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(10)
                    if row_idx == 0:
                        run.bold = True

            # Header row shading (light blue-gray)
            if row_idx == 0:
                set_cell_shading(cell, "D9E2F3")

    doc.add_paragraph()  # spacer
    return table


# ── main ─────────────────────────────────────────────────────────────────────

with open(INPUT, "r", encoding="utf-8") as f:
    md_lines = f.readlines()

doc = Document()

# ── Page setup ───────────────────────────────────────────────────────────────
for section in doc.sections:
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

# Default font
style = doc.styles["Normal"]
font = style.font
font.name = "Times New Roman"
font.size = Pt(12)
style.paragraph_format.line_spacing = 1.15

# ── Header / Footer ──────────────────────────────────────────────────────────
section = doc.sections[0]
header = section.header
hp = header.paragraphs[0]
hp.text = "Турбина Теслы — обзор"
for run in hp.runs:
    run.font.name = "Times New Roman"
    run.font.size = Pt(9)
    run.font.italic = True
hp.alignment = WD_ALIGN_PARAGRAPH.LEFT

footer = section.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = fp.add_run()
run.font.name = "Times New Roman"
run.font.size = Pt(9)

# Add page number field
fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
run._r.append(fldChar1)
instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
run._r.append(instrText)
fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
run._r.append(fldChar2)

# ── Parse markdown ───────────────────────────────────────────────────────────
# State machine: we go through lines, collect table lines separately, etc.

i = 0
n = len(md_lines)
title_processed = False

while i < n:
    line = md_lines[i]
    raw = line.rstrip("\n").rstrip("\r")

    # Skip blank lines at start
    if i == 0 and not raw.strip():
        i += 1
        continue

    # ── Horizontal rule ──────────────────────────────────────────────────
    if is_markdown_hr(raw) and len(raw.strip()) >= 3:
        # Add a thin horizontal rule via bottom border on empty para
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="999999"/>'
            f'</w:pBdr>'
        )
        pPr.append(pBdr)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        i += 1
        continue

    # ── Tables ───────────────────────────────────────────────────────────
    if is_markdown_table_line(raw):
        table_lines = [raw]
        i += 1
        while i < n and is_markdown_table_line(md_lines[i]):
            table_lines.append(md_lines[i].rstrip("\n").rstrip("\r"))
            i += 1
        rows = parse_table_rows(table_lines)
        if rows:
            render_table(doc, rows)
        continue

    # ── Bold subtitle line (like **Научно-популярный обзор**) ──────────
    # Match: **text** possibly with whitespace
    bold_match = re.match(r'^\s*\*\*(.+?)\*\*\s*$', raw)
    if bold_match:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(bold_match.group(1))
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        i += 1
        continue

    # ── Title (#) ────────────────────────────────────────────────────────
    title_match = re.match(r'^#\s+(.+)$', raw)
    if title_match and not title_processed:
        title_text = title_match.group(1)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title_text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        title_processed = True
        i += 1
        continue

    # ── Heading 2 (#### or ###) → Heading 2 ──────────────────────────────
    h2_match = re.match(r'^#{3,4}\s+(.+)$', raw)
    if h2_match:
        level = len(re.match(r'^(#+)', raw).group(1))
        h2_text = h2_match.group(1)
        p = doc.add_paragraph()
        # Add heading style
        run = p.add_run(h2_text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        i += 1
        continue

    # ── Heading 1 (##) ───────────────────────────────────────────────────
    h1_match = re.match(r'^#{2}\s+(.+)$', raw)
    if h1_match:
        h1_text = h1_match.group(1)
        p = doc.add_paragraph()
        run = p.add_run(h1_text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = 1.15
        i += 1
        continue

    # ── Regular paragraph ────────────────────────────────────────────────
    text = raw.strip()
    if not text:
        i += 1
        continue

    # Check for formulas (lines with math symbols like =, √, formulas)
    formula_keywords = ["v_rms", "U =", "p =", "τ_диск", "τ_столк", "Re =", "η =",
                        "√", "⋅", "·", "RPM", "p ="]

    is_formula = any(kw in text for kw in formula_keywords) and len(text.split()) <= 15

    if is_formula:
        add_formula_block(doc, text)
    else:
        p = doc.add_paragraph()
        # Handle inline bold (**...**)
        parts = re.split(r'(\*\*.+?\*\*)', text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run(part[2:-2])
                run.bold = True
            else:
                run = p.add_run(part)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    i += 1

# ── Save ─────────────────────────────────────────────────────────────────────
doc.save(OUTPUT)
print(f"✅ Done: {OUTPUT}")
