from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
# load PIL for resizing large images.
from StringIO import StringIO
from PIL import Image

# We'll use csv for bulk imports.
import csv

# Import models
from models import Team, RobotSpecs, RobotStrategy, MatchObservation, PracticeObservation, Observer

# import forms
import forms

def local (request):
	return request.META['REMOTE_ADDR'] == '127.0.0.1'

def root (request):
	'''
	This is the root view for interacting with Arcee.
	'''
	return render_to_response('root.html')

def admin (request):
	'''
	This is the root admin view for interacting with Arcee.
	'''
	# gatekeeper
	#return HttpResponse(request.META['REMOTE_ADDR'])
	if not local(request):
		return render_to_response('noaccess.html')
	
	return render_to_response('admin.html')
	
def add_observer (request):
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	if request.method == 'POST':
		form = forms.ObserverForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			# Choose post redirect action
			if request.POST.get('op', None) != 'Save and quit':
				form = forms.ObserverForm()
			else:
				return redirect('Profiling.views.admin')
	else:
		form = forms.ObserverForm()
	return render_to_response('upload.html', {
		'form': form,
		'messages': [],
		'title': 'Add Observer',
		'admin_page': True,
	},context_instance=RequestContext(request))
	
def uploadPhoto(request):
	'''
	This view is used for uploading photos
	'''
	if request.method == 'POST':
		form = forms.TeamPhotoForm(request.POST, request.FILES)
		if form.is_valid():
			team = form.cleaned_data['team']
			picture = form.cleaned_data['picture']
			# save the new uploaded photo.
			# DONE: delete the existing photo to prevent orphan files
			# DONE: Validate that an image was uploaded
			# TODO: Resize image to display size of 325x384 preserving aspect ratio
			
			im = Image.open(picture)
			im.thumbnail((325,384))
			im_file = StringIO()
			im.save(im_file, 'GIF')
			team.image.delete(save = False)
			team.image.save('%s/Team%d.gif' %(Team.IMAGE_PREFIX, team.number),ContentFile(im_file.getvalue()), save = True)
			
			# Choose post redirect action
			if request.POST.get('op', None) != 'Save and quit':
				form = forms.TeamPhotoForm()
			else:
				return redirect('Profiling.views.root')
	else:
		form = forms.TeamPhotoForm()
	return render_to_response('upload.html', {
		'form': form,
		'title': 'Upload Photo',
	},context_instance=RequestContext(request))

def import_pit_observations (request):
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	messages = []
	errors = []
	if request.method == 'POST':
		form = forms.ImportForm(request.POST, request.FILES)
		if form.is_valid():
			csv_data = form.cleaned_data['input']
			csv_file = csv.reader(csv_data)
			for row in csv_file:
				data = {}
				try:
					data['team'] = int(row[0])
				except:
					errors += ['A format error occured importing team data: %s is not an integer'%(row[0])]
					continue
				try:
					data['team'] = Team.objects.get(number = data['team'])
				except:
					errors += ['An import error occured: team %s not found' % (row[0])]
					continue
				try:
					data['stats'] = {}
					data['stats']['weight'] = float(row[1])
					data['stats']['height'] = float(row[2])
					data['stats']['length'] = float(row[3])
					data['stats']['width'] = float(row[4])
					data['stats']['drive_motor'] = row[5]
					data['stats']['drive_motor_qty'] = row[6]
					data['stats']['drive_wheels'] = row[7]
					data['stats']['total_wheels'] = row[8]
					data['stats']['speed'] = int(row[9])
					data['stats']['drv_team_practice_time'] = int(row[10])
					data['stats']['auto_strategy'] = row[11]
					data['stats']['auto_hang'] = [int(x) for x in row[12].split(',')]
					data['stats']['tele_hang'] = [int(x) for x in row[13].split(',')]
					data['stats']['tele_time_hang_bottom'] = int(row[14])
					data['stats']['tele_time_hang_middle'] = int(row[15])
					data['stats']['tele_time_hang_top'] = int(row[16])
					data['stats']['tele_strategy'] = row[17]
					data['stats']['pushing_power'] = int(row[18])
					data['stats']['mini_count'] = row[19]
					data['stats']['mini_speed'] = int(row[20])
					data['stats']['mini_deployment'] = int(row[21])
					data['stats']['mini_compat'] = None if row[22] == 'null' else True if row[22] == 'true' else False
					data['stats']['notes'] = row[23]
					data['strat']['strengths'] = row[24]
					data['strat']['weaknesses'] = row[25]
					data['strat']['strategy'] = row[26]
					data['strat']['auto_strategy'] = row[27]
				except:
					errors += ['A format error occured importing team %s'%(data['team'].number)]
					continue
				try:
					rsp = RobotSpecs.objects.get(team = data['team'])
					for prop in data['stats'].keys():
						setattr(rsp, prop, data['stats'][prop])
					rsp.full_clean()
				except ValidationError as e:
					errors += ['Team %d specs validation errors: %s' % e.message_dict]
					continue
				except:
					errors += ['A RobotSpecs model error occured importing team %s'%(data['team'].number)]
					continue
				try:
					rst = RobotStrategy.objects.get(team = data['team'])
					for prop in data['strat'].keys():
						setattr(rst, prop, data['strat'][prop])
					rst.full_clean()
				except ValidationError as e:
					errors += ['Team %d specs validation errors: %s' % e.message_dict]
					continue
				except:
					errors += ['A RobotSpecs model error occured importing team %s'%(data['team'].number)]
					continue
				try:
					rst = RobotStrategy.objects.get(team = data['team'])
				except:
					errors += ['A RobotStrategy error occured importing team %s'%(data['team'].number)]
				
			if len(errors) == 0:
				messages += ['All Observations imported successfully']
				if request.POST.get('op', None) != 'Save and quit':
					form = forms.ImportForm()
				else:
					return redirect('Profiling.views.admin')
	else:
		form = forms.ImportForm()
	return render_to_response('upload.html', {
		'form': form,
		'messages': messages,
		'errors': errors,
		'title': 'Import Pit Observations',
		'admin_page': True,
	},context_instance=RequestContext(request))

def bulk_import (request):
	'''
	Handles bulk import of team data
	'''
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	messages = []
	errors = []
	if request.method == 'POST':
		form = forms.ImportForm(request.POST, request.FILES)
		if form.is_valid():
			# Read and parse CSV data file.
			# Expected format:
			# "Team Number", "Team Name"[, "Team Location"[, "Team Sponsors"[, "Team Notes"]]]
			# TODO: Display expected format to web user.
			csv_data = form.cleaned_data['input']
			csv_file = csv.reader(csv_data)
			
			# We will use a single default image for the initial picture.
			picfile = open (settings.MEDIA_ROOT + '/'+Team.IMAGE_PREFIX+'/photo_not_available.gif', 'rb')
			try:
				for row in csv_file:
					# Read data, validating as we go, to build up team data dict.
					team_data = {}
					try:
						team_data['number'] = int(row[0])
					except ValueError:
						errors += ['Could not parse team number from "%s"' % row[0]]
						continue
					try:
						team_data['name'] = row[1]
					except IndexError:
						errors += ['Team name required for team %d' % team_number]
						continue
					if len(row) > 2:
						team_data['location'] = row[2]
					else:
						team_data['location'] = ''
					if len(row) > 3:
						team_data['sponsors'] = row[3]
					else:
						team_data['sponsors'] = ''
					if len(row) > 4:
						team_data['notes'] = row[4]
					else:
						team_data['notes'] = ''
					if len(row) > 5:
						messages += ['Ignoring extranious data for team %d.' % team_data['number']]
						
					# Validate team uniqueness.
					if Team.objects.filter(number = team_data['number']).exists():
						errors += ['A record already exists for team %d.' % team_data['number']]
						continue
						
					try:
						# Build and save models.Team, models.RobotSpecs, models.RobotStrategy for new team
						team = Team()
						team.number = team_data['number']
						team.name = team_data['name']
						team.location = team_data['location']
						team.sponsors = team_data['sponsors']
						team.notes = team_data['notes']
						team.image.save('%s/Team%d.gif' %(Team.IMAGE_PREFIX, team.number),File(picfile))
						team.full_clean()
						team.save()
						rst = RobotStrategy()
						rst.team = team
						rst.full_clean()
						rst.save()
						rsp = RobotSpecs()
						rsp.team = team
						rsp.full_clean()
						rsp.save()
					except Exception as e:
						errors += ['Format Error: L%d: %s' % (csv_file.line_num, e.message_dict if 'message_dict' in dir(e) else e)]
			except csv.Error as e:
				errors += ['CSV Format Error: L%d: %s' % (csv_file.line_num, e)]
			if len(errors) == 0:
				messages += ['All Teams imported successfully']
				if request.POST.get('op', None) != 'Save and quit':
					form = forms.ImportForm()
				else:
					return redirect('Profiling.views.admin')
	else:
		form = forms.ImportForm()
	return render_to_response('upload.html', {
		'form': form,
		'messages': messages,
		'errors': errors,
		'title': 'Import Teams',
		'admin_page': True,
	},context_instance=RequestContext(request))

def observer_import (request):
	'''
	Upload list of observers into the system
	'''
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	#TODO: allow creation of individual observers too.
	messages = []
	if request.method == 'POST':
		form = forms.ImportForm(request.POST, request.FILES)
		if form.is_valid():
			# Data is in a csv file for future expansion. Currently only observer name is stored.
			csv_data = form.cleaned_data['input']
			csv_file = csv.reader(csv_data)
			try:
				for row in csv_file:
					try:
						obs = Observer()
						obs.name = row[0]
						obs.save()
					except Exception as e:
						messages += ['file %s, line %d: %s<br/>' % (csv_data.name, csv_file.line_num, e.message_dict if 'message_dict' in dir(e) else e)]
			except csv.Error as e:
				messages += ['file %s, line %d: %s<br/>' % (csv_data.name, csv_file.line_num, e)]
			if len(messages) == 0:
				messages += ['All Observers imported successfully']
				if request.POST.get('op', None) != 'Save and quit':
					form = forms.ImportForm()
				else:
					return redirect('Profiling.views.admin')
	else:
		form = forms.ImportForm()
	return render_to_response('upload.html', {
		'form': form,
		'title': 'Import Observers',
		'messages': messages,
		'admin_page': True,
	},context_instance=RequestContext(request))
	

def ranking(request):
	'''
	Display team summaries based on various sortings
	'''
	
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	# Define a common comparator creator. Avoids tons of lambda statements
	def get_cmp (key):
		def cmp (a,b):
			a_ = getattr(a, key, 0)
			b_ = getattr(b, key, 0)
			return -1 if a_ < b_ else 0 if a_ == b_ else 1
		return cmp
			
	teams = list(Team.objects.all())
	# Third order sort
	teams.sort(cmp = get_cmp('max_match_score'), reverse = True)
	max_score = list(teams)
	#second order sort, preserves third because is stable sort
	teams.sort(cmp = get_cmp('ranking_score'), reverse = True)
	ranking = list(teams)
	#first order sort, preserves second because is stable sort
	teams.sort(cmp = get_cmp('qualification_score'), reverse = True)
	seeds = list(teams) # this is the FIRST Seed rank (we hope)
	teams.sort(cmp = get_cmp('average_alliance_score'), reverse = True)
	averages = list(teams)
	teams.sort(cmp = get_cmp('number'))
	numbers = list(teams)
	teams.sort(cmp = get_cmp('name'))
	names = list(teams)
	teams.sort(cmp = get_cmp('average_tube_hung'), reverse = True)
	tubes = list(teams)
	return render_to_response('rankings.html', {
		'seeds': seeds,
		'max_score': max_score,
		'ranking': ranking,
		'averages': averages,
		'numbers': numbers,
		'names': names,
		'tubes': tubes,
	})
	
	
def viewDefaultTeam (request):
	'''
	Redirect to the team with the lowest team number
	'''
	return redirect(Team.objects.all().order_by('number')[0])
	
def ShowTeam (request, number):
	'''
	Display detailed team information
	'''
	
	# grab read only data from the DB
	team = Team.objects.get(number=number)
	teams = Team.objects.all().order_by('number')
	prev_team = teams.filter(number__lt = number).order_by('-number')
	prev_team = prev_team[0].number if prev_team.count() else None
	next_team = teams.filter(number__gt = number).order_by('number')
	next_team = next_team[0].number if next_team.count() else None
	mobs = MatchObservation.objects.all().filter(team = team).order_by('match')
	pobs = PracticeObservation.objects.all().filter(team = team).order_by('time')
	messages = None
	
	#handle form information
	if request.method == 'POST':
		messages = []
		teamform = forms.TeamViewForm(request.POST, instance = team, prefix = 'Team')
		rsp = forms.RobotSpecsForm(request.POST, instance = RobotSpecs.objects.get(team = team), prefix = 'Specs')
		rst = forms.RobotStrategyForm(request.POST, instance = RobotStrategy.objects.get(team = team), prefix = 'Strategy')
		team_valid = teamform.is_valid()
		stats_valid = rsp.is_valid()
		strat_valid = rst.is_valid()
		if team_valid and stats_valid and strat_valid:
			teamform.save()
			rsp.save()
			rst.save()
			messages += ['Team %d saved.' % team.number]
		if not team_valid:
			messages += ['Errors were found in team information.']
		if not stats_valid:
			messages += ['Errors were found on specifications tab.']
		if not strat_valid:
			messages += ['Errors were found on strategy tab.']
	else:
		teamform = forms.TeamViewForm(instance = team, prefix = 'Team')
		rsp = forms.RobotSpecsForm(instance = RobotSpecs.objects.get(team = team), prefix = 'Specs')
		rst = forms.RobotStrategyForm(instance = RobotStrategy.objects.get(team = team), prefix = 'Strategy')
	return render_to_response('view_team.html',{
			'messages': messages,
			'team': team,
			'teams': teams,
			'teamform': teamform,
			'robot_specs': rsp,
			'robot_strategy': rst,
			'prev_team': prev_team,
			'next_team': next_team,
			'match_observations': mobs,
			'practice_observations': pobs,
		},context_instance=RequestContext(request))

def NewMatchObservation (request):
	'''
	Enter a new match observation. Remember the last observer to enter an observation, they'll probably enter anotehr one.
	'''
	initial_data = {
		'observer': request.session.get('observer', ''),
	}
	if request.method == 'POST':
		mob = forms.NewMatchObservationForm(request.POST, request.FILES)
		if mob.is_valid():
			request.session['observer'] = mob.cleaned_data['observer'].pk
			initial_data['observer'] = request.session['observer']
			mob.save()
			if request.POST.get('op', None) != 'Save and quit':
				mob = forms.NewMatchObservationForm(initial=initial_data)
			else:
				return redirect('Profiling.views.root')
	else:
		mob = forms.NewMatchObservationForm(initial=initial_data)
	return render_to_response('add_match_observation.html',{
			'match_observation': mob,
		},context_instance=RequestContext(request))

def NewPracticeObservation (request):
	'''
	Enter a new practice match observation. Remember the last observer to enter an observation, they'll probably enter anotehr one.
	'''
	initial_data = {
		'observer': request.session.get('observer', ''),
	}
	if request.method == 'POST':
		pob = forms.NewPracticeObservationForm(request.POST, request.FILES)
		if pob.is_valid():
			request.session['observer'] = pob.cleaned_data['observer'].pk
			initial_data['observer'] = request.session['observer']
			pob.save()
			if request.POST.get('op', None) != 'Save and quit':
				pob = forms.NewPracticeObservationForm(initial=initial_data)
			else:
				return redirect('Profiling.views.root')
	else:
		pob = forms.NewPracticeObservationForm(initial=initial_data)
	return render_to_response('add_practice_observation.html',{
			'practice_observation': pob,
		},context_instance=RequestContext(request))
		
def team_pdf (request):
	# gatekeeper
	if not local(request):
		return render_to_response('noaccess.html')
	
	if request.method == 'POST':
		form = forms.PDFForm(request.POST)
		if form.is_valid():
			from generatepdf import build_document
			team = form.cleaned_data['teams'] if len(form.cleaned_data['teams']) > 0 else None
			response = HttpResponse(mimetype='application/pdf')
			build_document(response, team)
			return response
	else:
		form = forms.PDFForm()
	return render_to_response('upload.html', {
		'form': form,
		'messages': None,
		'errors': None,
		'title': 'Generate Profiling PDFs',
		'admin_page': True,
	},context_instance=RequestContext(request))
#	from generatepdf import build_document
#	team = Team.objects.get(number=int(number))
#	response = HttpResponse(mimetype='application/pdf')
#	#response['Content-Disposition'] = 'attachment; filename=Arcee Team %d.pdf' % team.number
#	
#	build_document(response, team)
#	return response
	
