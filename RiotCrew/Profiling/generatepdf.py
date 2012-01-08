from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from xml.sax.saxutils import escape

from django.db import models
from Profiling.models import Team, RobotSpecs, RobotStrategy

PAGE_HEIGHT=letter[1]; PAGE_WIDTH=letter[0]

pStyle = ParagraphStyle({
	'fontSize': 10,
	'leading': 10,
})
tStyle = ParagraphStyle({
	'fontSize': 10,
	'leading': 10,
	'spaceAfter': 7,
})
hStyle = getSampleStyleSheet()['Heading3']

def page_layout(canvas, doc):
	pageinfo = "Arcee Team Profiling"
	canvas.saveState()
	canvas.drawString(inch, PAGE_HEIGHT - (0.25 * inch), 'Arcee Team Profiling')
	canvas.setFont('Times-Roman',8)
	canvas.drawString(inch, 0.25 * inch, "Page %d %s" % (doc.page, pageinfo))
	canvas.restoreState()

def _choose_columns (options):
	width = 75
	def chk_length(n):
		idx = 0
		lth = 0
		for opt in options:
			lth += 1 + len(opt)
			idx += 1
			if lth > width:
				return False
			if idx >= n:
				idx = 0
				lth = 0
		return True
	cols = width / 2 if width /2 < len(options) else len(options)
	while cols > 1 and not chk_length(cols):
		cols -= 1
	return cols 
	
def _col_widths (options, ncols):
	widths = []
	for i in range(0,ncols):
		widths.append(max([len(o) for o in options[i::ncols]]))
	return widths
	
def _ChoiceField_to_empty_row (model, field):
	field_name = field.verbose_name if field.verbose_name else field.name
	opts = [o[1] for o in field.choices]
	opt_cols = _choose_columns (opts)
	content = []
	row = []
	for opt in [ escape(o) for o in opts]:
		if len(row) >= opt_cols:
			content.append(row)
			row = []
		row.append('%s' %(opt))
	content.append(row)
	content = Table(content)
	content.setStyle(TableStyle([
		('RIGHTPADDING', (0,0), (-1,-1),0), 
		('TOPPADDING', (0,0), (-1,-1),0), 
		('BOTTOMPADDING', (0,0), (-1,-1), 0)
	]))
	return [Paragraph('<b>%s:</b>' %escape(field_name),pStyle), content] 

def _CharField_to_empty_cell (model, field):
	field_name = field.verbose_name if field.verbose_name else field.name
	p = Paragraph('<b>%s:</b>' % escape(field_name),pStyle)
	if isinstance(field, models.TextField):
		return [p, Spacer(0, 0.85*inch)]
	else:
		return p

def _CharField_to_data_cell (model, field):
	field_name = field.verbose_name if field.verbose_name else field.name
	p = Paragraph('<b>%s:</b> %s' % (escape(field_name), escape(str(getattr(model, field.name)))),pStyle)
	return p

def _pad_row (row, cols):
	if (len(row)):
		while len(row) < cols:
			row.append('')
	return row
	
def _model_to_rows(model, columns=4, exclude=None, include=None, data = False):
	cols = [
		[2*inch, 6*inch], # Multiple select field
		[8*inch],
		[4*inch]*2,
		[2.66*inch]*3,
		[2*inch]*4,
		[1.6*inch]*5,
		[1.33*inch]*6,
		[1.14*inch]*7,
		[1*inch]*8,
	]
	cells = []
	row=[]
	sections = getattr(model,'ARCEE_SECTIONS',None)
	for field in model._meta.fields:
		if exclude and field.name in exclude:
			continue
		if include and field.name not in include:
			continue
		if sections and field.name in sections.keys():
			if (len(row)):
				cells.append((_pad_row(row, columns),cols[columns]))
				row = []
			cells.append(([Paragraph('<u><i><b>%s</b></i></u>' % sections[field.name], hStyle)],cols[1]))
		if len(row) >= columns:
			cells.append((row,cols[columns]))
			row = []
		#if field.choices and not data:
		#	# multiple choice forces a new row.
		#	if (len(row)):
		#		cells.append((_pad_row(row, columns),cols[columns]))
		#		row = []		
		#	cells.append((_ChoiceField_to_empty_row(model, field), cols[0]))
		#	row = []
		#else:
		if data:
			row.append(_CharField_to_data_cell(model, field))
		else:
			row.append(_CharField_to_empty_cell(model, field))
	if len(row):
		cells.append((_pad_row(row, columns), cols[columns]))
	return cells
	
def _build_page(rows):
	page = []
	for row in rows:
		t=Table([row[0]], colWidths=row[1])
		t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
		page.append(t)
	page.append(PageBreak())
	return page
	
def build_story(team):
	# Grab related data
	specs = RobotSpecs.objects.get(team=team)
	strat = RobotStrategy.objects.get(team=team)
	
	#begin building 'chapter' Team specs on page 1, team strategy on page 2
	chapter = []
	rows = _model_to_rows(team, 3, include=['number','name','robotname'], data = True)
	rows += _model_to_rows(specs, 3, exclude=['id', 'team', 'notes'])
	rows += _model_to_rows(strat, 1, exclude=['id', 'team'])
	rows += _model_to_rows(specs, 1, include=['notes'])
	chapter += _build_page(rows)
	return chapter

def build_document (file, teams = None, data = False, observations = False):
	doc = SimpleDocTemplate(file,
		pagesize = letter,
		leftMargin = 0.5 * inch,
		rightMargin = 0.5 * inch,
		topMargin = 0.5 * inch,
		bottomMargin = 0.5 * inch,
		)
	Story = []
	if teams:
		if getattr (teams, '__iter__', None):
			# list like object
			for team in teams:
				Story += build_story (team)
		else:
			Story += build_story(teams)
	else:
		for team in Team.objects.all().order_by('number'):
			Story += build_story(team)
	doc.build(Story, onFirstPage=page_layout, onLaterPages=page_layout)