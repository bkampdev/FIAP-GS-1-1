"""Gera o relatório paginado da GS a partir da fonte em Markdown."""
import re
import sys
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

INK = colors.HexColor('#152C3D')
TEAL = colors.HexColor('#155B64')
LIGHT = colors.HexColor('#F0F5F6')
MUTED = colors.HexColor('#4C6574')
MARGIN = 52
WIDTH = A4[0] - 2 * MARGIN
TITLE = 'Neighborhood Action Dashboard'

styles = {
    'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=27,
                            leading=31, textColor=INK, spaceAfter=19),
    'heading': ParagraphStyle('heading', fontName='Helvetica-Bold', fontSize=22,
                              leading=26, textColor=INK, spaceAfter=20),
    'subheading': ParagraphStyle('subheading', fontName='Helvetica-Bold',
                                 fontSize=13, leading=17, textColor=TEAL,
                                 spaceBefore=8, spaceAfter=8, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=11,
                           leading=17, textColor=INK, spaceAfter=10, alignment=TA_LEFT),
    'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=11,
                             leading=16, textColor=INK, leftIndent=15, spaceAfter=5),
    'cell': ParagraphStyle('cell', fontName='Helvetica', fontSize=9.3,
                           leading=12.5, textColor=INK),
    'headercell': ParagraphStyle('headercell', fontName='Helvetica-Bold',
                                 fontSize=9.3, leading=12.5, textColor=colors.white),
    'code': ParagraphStyle('code', fontName='Courier', fontSize=9,
                           leading=13, textColor=TEAL, spaceAfter=3),
}

def inline(text):
    text = escape(text.replace('→', ' > ').replace('–', '-').replace('—', '-'))
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
                  r'<link color="#155B64" href="\2">\1</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)

def paragraph(text, style='body'):
    return Paragraph(inline(text), styles[style])

def render_table(lines):
    rows = [item.strip().strip('|').split('|') for item in lines]
    rows = [row for row in rows if not all(re.fullmatch(r'\s*:?-+:?\s*', c) for c in row)]
    data = [[paragraph(cell.strip(), 'headercell' if i == 0 else 'cell')
             for cell in row] for i, row in enumerate(rows)]
    table = Table(data, colWidths=[WIDTH / len(rows[0])] * len(rows[0]), repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    return table

def compose(text):
    story, table = [], []
    code, sections = False, 0
    content = []
    def flush():
        if content:
            story.append(paragraph(' '.join(content)))
            content.clear()
        if table:
            story.extend([render_table(table), Spacer(1, 12)])
            table.clear()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith('|') and not code:
            if content:
                flush()
            table.append(line)
        elif line.startswith('```'):
            flush()
            code = not code
        elif code:
            story.append(paragraph(raw_line.replace(' ', '\u00a0'), 'code'))
        elif line.startswith('## '):
            flush()
            if sections:
                story.append(PageBreak())
            story.append(paragraph(line[3:], 'heading'))
            sections += 1
        elif line.startswith(('### ', '# ')):
            flush()
            prefix, _, title = line.partition(' ')
            story.append(paragraph(title, 'title' if prefix == '#' else 'subheading'))
        elif line.startswith(('- ', '* ')):
            flush()
            story.append(Paragraph(inline(line[2:]), styles['bullet'], bulletText='•'))
        elif line:
            if table:
                flush()
            content.append(line)
        else:
            flush()
    flush()
    return story

def decorate(canvas, doc):
    canvas.saveState()
    canvas.setTitle(TITLE)
    canvas.setAuthor('Grupo 2 — FIAP')
    canvas.setFillColor(TEAL)
    canvas.rect(MARGIN, A4[1] - 39, 22, 3.5, stroke=0, fill=1)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(MARGIN + 31, A4[1] - 40, 'FIAP  /  GLOBAL SOLUTION 2026.2')
    canvas.setStrokeColor(LIGHT)
    canvas.line(MARGIN, 43, A4[0] - MARGIN, 43)
    canvas.setFillColor(MUTED)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(MARGIN, 28, 'CitizenTech  /  Grupo 2')
    canvas.drawRightString(A4[0] - MARGIN, 28, str(doc.page))
    canvas.restoreState()

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "docs" / "relatorio.md"
target = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "docs" / "relatorio.pdf"
doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=MARGIN,
                        rightMargin=MARGIN, topMargin=66, bottomMargin=60,
                        allowSplitting=True)
doc.build(compose(source.read_text()), onFirstPage=decorate, onLaterPages=decorate)
