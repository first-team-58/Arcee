import ArceeFields

from django.db import models
from django.core.files import File
# Create your models here.
class Team (models.Model):
	IMAGE_PREFIX = 'Images/Robots'
	number = models.PositiveIntegerField (
		primary_key = True,
		verbose_name = 'Team Number',
	)
	name = models.CharField (
		max_length = 200,
		default = 'Not Recorded',
		verbose_name = 'Team Name',
	)
	image = models.ImageField(
		upload_to = IMAGE_PREFIX,
		verbose_name = 'Robot Picture'
	)
	robotname = models.CharField(
		blank = True,
		max_length = 200,
		verbose_name = 'Robot Name',
	)
	sponsors = models.TextField (
		blank = True,
		default = 'Not Recorded',
		verbose_name = 'School/Sponsors',
	)
	location = models.CharField (
		max_length = 200,
		blank = True,
		default = 'Not Recorded',
		verbose_name = 'Location',
	)
	
	def __init__ (self, *args, **kwargs):
		super(Team, self).__init__(*args, **kwargs)
		self.red_cards = 0
		self.yellow_cards = 0
		if (self.number):
			matches = list(MatchObservation.objects.all().filter(team=self))
			tot_rank = 0
			tot_qual = 0
			tot_ally = 0
			tot_opp = 0
			tot_tubes = 0
			for m in matches:
				tot_rank += m.ranking_score()
				tot_qual += m.qualification_score()
				tot_ally += m.alliance_points()
				tot_opp += m.opponent_points()
				self.red_cards += 1 if m.disqualified() else 0
				self.yellow_cards += 1 if m.warning() else 0
				tot_tubes += m.tele_hung_qty
			self.ranking_score = float(tot_rank)/float(len(matches)) if len(matches) > 0 else 0
			self.qualification_score = tot_qual if len(matches) > 0 else 0
			self.max_match_score = max([m.alliance_points() for m in matches]) if len(matches) > 0 else 0
			self.matches_played = len(matches)
			self.average_alliance_score = float(tot_ally)/float(len(matches)) if len(matches) > 0 else 0
			self.average_opponent_score = float(tot_opp)/float(len(matches)) if len(matches) > 0 else 0
			self.average_tubes_hung = float(tot_tubes)/len(matches) if len(matches) else 0
		else:
			self.ranking_score = 0
			self.qualification_score = 0
			self.max_match_score = 0
			self.matches_played = 0
			self.average_alliance_score = 0
			self.average_opponent_score = 0
			self.average_tubes_hung = 0
		
	@models.permalink
	def get_absolute_url(self):
		return ('Profiling.views.ShowTeam',(), {'number': self.number})
	
	def __unicode__ (self):
		return u'%d - %s' % (self.number, self.name)


class RobotStrategy (models.Model):
	ARCEE_SECTIONS = {
		'strengths': 'Team Strategy',
	}
	team = models.OneToOneField(Team,
		editable = False,
		verbose_name = 'Team',
	)
	strengths = models.TextField (
		blank = True,
		verbose_name = 'Strengths',
	)
	weaknesses = models.TextField (
		blank = True,
		verbose_name = 'Weaknesses'
	)
	strategy = models.TextField (
		blank = True,
		verbose_name = 'Strategy'
	)
	auto_strategy = models.TextField (
		blank = True,
		verbose_name = 'Hybrid Strategy'
	)
	

class RobotSpecs (models.Model):
	ARCEE_SECTIONS = {
			'weight': 'Basic Stats',
			'auto_strategy': 'Hybrid',
			'tele_hang': 'Teleoperation',
		}
	NBOOL_CHOICES = (
		(None, 'Unknown'),
		(True, 'Yes'),
		(False, 'No'),
	)
	MOTOR_TYPES = (
		('NSP', 'Not Specified'),
		('N/A', 'Not Applicable'),
		('CIM', 'CIM'),
		('BNE', 'Bane Bot'),
		('FP', 'Fischer Price'),
		('WND', 'Window Motor'),
		('CMB', 'Combination')
	)
	QUANTITY = (
		('Z','N/A'),
		('0','0'),
		('1','1'),
		('2','2'),
		('3','3'),
		('4','4'),
		('5','5'),
		('6','6'),
		('7','7'),
		('8','8'),
		('9','9'),
		('A','10')
	)
	PRACTICE_TIME = (
		(0, 'N/A'),
		(1, '1 Day'),
		(2, '2 Days'),
		(3, '3 Days'),
		(4, '4 Days'),
		(5, '5 Days'),
		(6, '6 Days'),
		(7, '7 Days'),
		(8, '8 Days'),
		(9, '9 Days'),
		(10, '10 Days'),
		(11, '11 Days'),
		(12, '12 Days'),
		(13, '13 Days'),
		(14, '14 Days'),
		(15, '15 Days'),
		(16, '16 Days'),
		(17, '17 Days'),
		(18, '18 Days'),
		(19, '19 Days'),
		(20, '20 Days'),
		(21, '21 Days'),
		(22, '22+ Days'),
		)
	GAME_TIME = (
		(0, 'N/A'),
		(1, '1 sec'),
		(2, '2 sec'),
		(3, '3 sec'),
		(4, '4 sec'),
		(5, '5 sec'),
		(6, '6 sec'),
		(7, '7 sec'),
		(8, '8 sec'),
		(9, '9 sec'),
		(10, '10 sec'),
		(11, '11 sec'),
		(12, '12 sec'),
		(13, '13 sec'),
		(14, '14 sec'),
		(15, '15 sec'),
		(16, '16 sec'),
		(17, '17 sec'),
		(18, '18 sec'),
		(19, '19 sec'),
		(20, '20 sec'),
		(21, '21+ sec'),
	)
	AUTO_STRATEGY = (
		('NOA', 'No Action'),
		('HOB', 'Score Bottom'),
		('HOM', 'Score Middle'),
		('HOT', 'Score Top'),
		('POS', 'Position Robot'),
	)
	ROWS = (
		('3', 'Top'),
		('2', 'Middle'),
		('1', 'Bottom'),
	)
	TELE_STRATEGY = (
		('NOP', 'Not Provided',),
		('HNG', 'Score Baskets'),
		('BLK', 'Blocking Defense'),
		('HAR', 'Harrassing Defense'),
		('OTO', 'Other')
	)
	POWER = (
		(0, 'Not Provided'),
		(1, 'Can\'t Push'),
		(2, 'Hold Bot'),
		(3, 'Pushes Bot'),
	)
	team = models.OneToOneField(Team,
		editable = False,
		verbose_name = 'Team',
	)
	weight = models.DecimalField (
		default = '0.0',
		max_digits = 5,
		decimal_places = 2,
		verbose_name = 'Weight',
		help_text = 'Total Robot Weight (lbs)',
	)
	height = models.DecimalField (
		default = '0.0',
		max_digits = 6,
		decimal_places = 2,
		verbose_name = 'Height',
		help_text = 'Robot height (inches)',
	)
	length = models.DecimalField (
		default = '0.0',
		max_digits = 5,
		decimal_places = 2,
		verbose_name = 'Length',
		help_text = 'Robot length from front to back (inches)',
	)
	width = models.DecimalField (
		default = '0.0',
		max_digits = 5,
		decimal_places = 2,
		verbose_name = 'Width',
		help_text = 'Robot width across front (inches)',
	)
	drive_motor = models.CharField(
		default = 'NSP',
		choices = MOTOR_TYPES,
		max_length = 3,
		verbose_name = 'Drive Motor',
		help_text = 'Primary drive motor type',
	)
	drive_motor_qty = models.CharField (
		default = 'Z',
		choices = QUANTITY,
		max_length = 1,
		verbose_name = 'Drive Motor Quantity',
		help_text = 'Total number of driving motors',
	)
	drive_wheels = models.CharField (
		default = 'Z',
		choices = QUANTITY,
		max_length = 1,
		verbose_name = 'Drive Wheels',
		help_text = 'Number of wheels receiving power',
	)
	total_wheels = models.CharField (
		default = 'Z',
		choices = QUANTITY,
		max_length = 1,
		verbose_name = 'Total Wheels',
		help_text = 'Total number of wheels',
	)
	speed = models.IntegerField (
		default = -1,
		verbose_name = 'Robot Speed',
		help_text = 'Time from feeding station to far wall at full speed (seconds)',
	)
	drv_team_practice_time = models.IntegerField (
		default = 0,
		choices = PRACTICE_TIME,
		verbose_name = 'Drive Team Practice Time',
		help_text = 'Time spent practicing with this year\'s robot.',
	)
	hybrid_strategy = models.CharField (
		max_length = 3,
		default = 'NOA',
		choices = AUTO_STRATEGY,
		verbose_name = 'Hybrid Strategy',
		help_text = 'Preferred or best hybrid mode strategy',
	)
	hybrid_score = ArceeFields.MultiSelectField (
		blank = True,
		max_length = 20,
		choices = ROWS,
		verbose_name = 'Robot can score baskets',
		help_text = 'Robot can score baskets on these levels in autonomous mode',
	)
	tele_score = ArceeFields.MultiSelectField (
		blank = True,
		max_length = 20,
		choices = ROWS,
		verbose_name = 'Robot can score baskets',
		help_text = 'Robot can score baskets on these levels in teleoperation mode',
	)
	tele_time_score_bottom = models.IntegerField (
		default = 0,
		choices = GAME_TIME,
		verbose_name = 'Time to score bottom basket',
		help_text = 'Time to score bottom basket with scoring mechanism starting in rest state',
	)
	tele_time_score_middle = models.IntegerField (
		default = 0,
		choices = GAME_TIME,
		verbose_name = 'Time to score middle basket',
		help_text = 'Time to score middle basket with scoring mechanism starting in rest state',
	)
	tele_time_score_top = models.IntegerField (
		default = 0,
		choices = GAME_TIME,
		verbose_name = 'Time to score top basket',
		help_text = 'Time to score top basket with scoring mechanism starting in rest state',
	)
	tele_strategy = models.CharField (
		max_length = 3,
		default = 'NOP',
		choices = TELE_STRATEGY,
		verbose_name = 'Prefered Strategy',
		help_text = 'Preferred or best teleoperation mode strategy',
	)
	pushing_power = models.IntegerField (
		default = 0,
		choices = POWER,
		verbose_name = 'Pushing Power',
		help_text = 'Robot relative pushing power',
	)
	balance_capable = models.NullBooleanField (
		default = None,
		choices = NBOOL_CHOICES,
		verbose_name = 'Robot can balance',
		help_text = 'Robot can balance on a bridge at the end of the match',
	)
	multi_balance_capable = models.NullBooleanField (
		default = None,
		choices = NBOOL_CHOICES,
		verbose_name = 'Robot can multi-balance',
		help_text = 'Robot can ballance on a bridge with one or more other robots on the bridge at the end of the match',
	)
	notes = models.TextField (
		blank = True,
		verbose_name = 'Additional Notes'
	)
	
class MatchObservation (models.Model):
	HYBRID_ACTIONS = (
		('NOA', 'No Activity'),
		('HOB', 'Scored Bottom'),
		('HOM', 'Scored Middle'),
		('HOT', 'Scored Top'),
		('HAT', 'Attempted Score'),
		('OTO', 'Other'),
	)
	TELE_SCORE = (
		(0, 'None'),
		(2, '1-3 Baskets'),
		(5, '4-6 Baskets'),
		(8, '7-9 Baskets'),
		(11, '10-12 Baskets'),
	)
	TELE_COLLECT = (
		('N/A', 'Not Applicable'),
		('STA', 'Feeding Station'),
		('GND', 'Ground'),
		('BOT', 'Both'),
	)
	SPEED = (
		('NOM', 'No Movement'),
		('VSL', 'Very Slow'),
		('SLO', 'Slow'),
		('AVG', 'Average'),
		('FST', 'Fast'),
		('SPD', 'Speedy Gonzolas'),
	)
	RED_YELLOW_CARDS = (
		('NON', 'No Cards'),
		('YLW', 'Yellow Card'),
		('RED', 'Red Card'),
		('BOT', 'Yellow+Red Card'),
	)
	QUANTITY = (
		('Z','N/A'),
		('0','0'),
		('1','1'),
		('2','2'),
		('3','3'),
		('4','4'),
		('5','5'),
		('6','6'),
		('7','7'),
		('8','8'),
		('9','9'),
		('A','10')
	)
	team = models.ForeignKey ( Team,
		verbose_name = 'Team',
	)
	match = models.PositiveIntegerField (
		verbose_name = 'Match number',
	)
	observer = models.ForeignKey ( 'Observer',
		verbose_name = 'Observer',
	)
	alliance_score = models.IntegerField (
		verbose_name = 'Alliance Score',
	)
	opponent_score = models.IntegerField (
		verbose_name = 'Opponent Score',
	)
	alliance_penalties = models.IntegerField (
		verbose_name = 'Alliance Fouls',
	)
	opponent_penalties = models.IntegerField (
		verbose_name = 'Opponent Fouls',
	)
	alliance_tech_penalties = models.IntegerField (
		verbose_name = 'Alliance Technical Fouls',
	)
	opponent_tech_penalties = models.IntegerField (
		verbose_name = 'Opponent Technical Fouls',
	)
	red_yellow_card = models.CharField ( 
		default = 'NON',
		max_length = 3,
		choices = RED_YELLOW_CARDS,
		verbose_name = 'Team Earned Red/Yellow Card',
	)
	auto_action = models.CharField ( 
		default = 'NOA',
		max_length = 3,
		choices = HYBRID_ACTIONS,
		verbose_name = 'Hybrid Action',
	)
	tele_hung_qty = models.IntegerField (
		default = 'N/A',
		choices = TELE_SCORE,
		verbose_name = 'Baskets Scored',
	)
	tele_hung = ArceeFields.MultiSelectField (
		blank = True,
		max_length = 20,
		choices = RobotSpecs.ROWS,
		verbose_name = 'Robot scored baskets',
		help_text = 'Robot scored in these baskets in teleoperation mode',
	)
	tele_collected = models.CharField (
		max_length = 3,
		default = 'N/A',
		choices = TELE_COLLECT,
		verbose_name = 'Balls Collected From',
	)
	tele_dropped = models.IntegerField (
		default = 'N/A',
		choices = TELE_SCORE,
		verbose_name = 'Lost Balls(s)',
	)
	tele_damaged = models.IntegerField (
		default = 'N/A',
		choices = TELE_TUBES,
		verbose_name = 'Damaged Balls(s)',
	)
	tele_strategy = models.CharField (
		max_length = 3,
		default = 'NOP',
		choices = RobotSpecs.TELE_STRATEGY,
		verbose_name = 'Robot Strategy',
	)
	speed = models.CharField (
		max_length = 3,
		default = 'NOM',
		choices = SPEED,
		verbose_name = 'Robot Speed',
	)
	balance_capable = models.NullBooleanField (
		default = None,
		choices = RobotSpecs.NBOOL_CHOICES,
		verbose_name = 'Robot balanced',
		help_text = 'Robot balanced on a bridge at the end of the match',
	)
	notes = models.TextField (
		blank = True,
		verbose_name = 'Additional Notes'
	)
	def alliance_points(self):
		sc = self.alliance_score + self.opponent_penalties * 3 + self.opponent_tech_penalties * 9
		return sc if sc > 0 else 0
		
	def opponent_points(self):
		sc = self.opponent_score + self.alliance_penalties * 3 + self.alliance_tech_penalties * 9
		return sc if sc > 0 else 0
		
	def result(self):
		my_score = self.alliance_points()
		their_score = self.opponent_points()
		return 'Win' if my_score > their_score else 'Tie' if my_score == their_score else 'Lose'
	def warning(self):
		return self.red_yellow_card in ['YLW', 'BOT']
	def disqualified (self):
		return self.red_yellow_card in ['RED', 'BOT']
	def qualification_score(self):
		if self.disqualified():
			return 0
		my_score = self.alliance_points()
		their_score = self.opponent_points()
		return 2 if my_score > their_score else 1 if my_score == their_score else 0
		
	def ranking_score(self):
		if self.disqualified():
			return 0
		my_score = self.alliance_points()
		their_score = self.opponent_points()
		return self.opponent_score if my_score > their_score else my_score
	
	def __unicode__(self):
		return u'MO%d:%d' %(self.team.number, self.match)

class PracticeObservation (models.Model):
	MINI_SCORE = (
		(0, 'No Score'),
		(1, 'Scores'),
	)
	team = models.ForeignKey ( Team,
		verbose_name = 'Team',
	)
	time = models.DateTimeField(
		auto_now_add = True,
		editable = False,
		verbose_name = "Match Time",
	)
	observer = models.ForeignKey ( 'Observer',
		verbose_name = 'Observer',
	)
	auto_action = models.CharField ( 
		default = 'NOA',
		max_length = 3,
		choices = HYBRID_ACTIONS,
		verbose_name = 'Hybrid Action',
	)
	tele_hung_qty = models.IntegerField (
		default = 'N/A',
		choices = TELE_SCORE,
		verbose_name = 'Baskets Scored',
	)
	tele_hung = ArceeFields.MultiSelectField (
		blank = True,
		max_length = 20,
		choices = RobotSpecs.ROWS,
		verbose_name = 'Robot scored baskets',
		help_text = 'Robot scored in these baskets in teleoperation mode',
	)
	tele_collected = models.CharField (
		max_length = 3,
		default = 'N/A',
		choices = TELE_COLLECT,
		verbose_name = 'Balls Collected From',
	)
	tele_dropped = models.IntegerField (
		default = 'N/A',
		choices = TELE_SCORE,
		verbose_name = 'Lost Balls(s)',
	)
	tele_damaged = models.IntegerField (
		default = 'N/A',
		choices = TELE_TUBES,
		verbose_name = 'Damaged Balls(s)',
	)
	tele_strategy = models.CharField (
		max_length = 3,
		default = 'NOP',
		choices = RobotSpecs.TELE_STRATEGY,
		verbose_name = 'Robot Strategy',
	)
	speed = models.CharField (
		max_length = 3,
		default = 'NOM',
		choices = SPEED,
		verbose_name = 'Robot Speed',
	)
	balance_capable = models.NullBooleanField (
		default = None,
		choices = RobotSpecs.NBOOL_CHOICES,
		verbose_name = 'Robot balanced',
		help_text = 'Robot balanced on a bridge',
	)
	notes = models.TextField (
		blank = True,
		verbose_name = 'Additional Notes'
	)
	def __unicode__(self):
		return u'PO%d:%d' %(self.team.number, self.time)

class Observer (models.Model):
	name = models.CharField(
		max_length = 50,
		unique = True,
	)
	def __unicode__(self):
		return '%s' % self.name
	
