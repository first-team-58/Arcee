
from django import forms
from models import Team, RobotSpecs, RobotStrategy, MatchObservation, PracticeObservation, Observer

class PDFForm (forms.Form):
	teams = forms.ModelMultipleChoiceField(
		label='Choose teams, leave blank for all teams',
		required = False,
		queryset = Team.objects.all().order_by('number'),
		#empty_label = 'All teams',
	)
	
class ImportForm (forms.Form):
	input = forms.FileField (
		label = 'Choose file to import',
		widget = forms.FileInput(attrs={'accept':'text/csv'}),
	)

class TeamPhotoForm (forms.Form):
	team = forms.ModelChoiceField(
		queryset = Team.objects.all().order_by('number'),
		empty_label = 'Select Team',
	)
	picture = forms.FileField (
		label = 'Choose team photo',
		widget = forms.FileInput(attrs={'accept':'image/*'}),
	)
	
class TeamViewForm (forms.ModelForm):
	class Meta:
		model = Team
		exclude = ('image', 'number')
			
class TeamForm (forms.ModelForm):
	class Meta:
		model = Team

class RobotStrategyForm (forms.ModelForm):
	class Meta:
		model = RobotStrategy

class RobotSpecsForm (forms.ModelForm):
	class Meta:
		model = RobotSpecs
		widgets = {
			'auto_hang': forms.CheckboxSelectMultiple,
			'tele_hang': forms.CheckboxSelectMultiple,
		}
	
class MatchObservationForm (forms.ModelForm):
	class Meta:
		model = MatchObservation
		exclude = ('team')

	
class NewMatchObservationForm (forms.ModelForm):
	team = forms.ModelChoiceField(
		queryset = Team.objects.all().order_by('number'),
		empty_label = 'Select Team',
	)
	observer = forms.ModelChoiceField(
		queryset = Observer.objects.all().order_by('name'),
		empty_label = 'Select Observer',
	)
	class Meta:
		model = MatchObservation
		
class PracticeObservationForm (forms.ModelForm):
	class Meta:
		model = PracticeObservation
		exclude = ('team')

class NewPracticeObservationForm (forms.ModelForm):
	team = forms.ModelChoiceField(
		queryset = Team.objects.all().order_by('number'),
		empty_label = 'Select Team',
	)
	observer = forms.ModelChoiceField(
		queryset = Observer.objects.all().order_by('name'),
		empty_label = 'Select Observer',
	)
	class Meta:
		model = PracticeObservation

class ObserverForm (forms.ModelForm):
	class Meta:
		model = Observer
		
class NewObserverForm (forms.ModelForm):
	class Meta:
		model = Observer
