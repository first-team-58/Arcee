from django import template

'''
Arcee_tags: Extra tags to implement commonly used template patterns.

Based on examples ant techniques found at:
http://docs.djangoproject.com/en/1.2/howto/custom-template-tags
'''

register = template.Library()

@register.inclusion_tag('snippits/buttons.html')
def form_save_buttons (root_link = None):
	'''
	Include the standard 'Save and Continue', 'Save and Quit', and 'Quit' 
	buttons.
	
	Uses Template: 'snippits/buttons.html
	
	Tag Definition: {% form_save_buttons %}
	Example: {% form_save_buttons %}
	'''
	return {'root_link': root_link}

@register.inclusion_tag('snippits/messages.html')
def show_messages (messages, errors = False):
	'''
	Format a list of messages for display in web forms.
	
	Uses Template: 'snippits/messages.html'
	
	Tag Parameters:
		errors: 'true' if messages are errors else 'false' (default: 'false')
	
	Tag Definition: {% show_messages messages [errors='false'] %}
	Example: {% show_messages form_validation_errors 'true' %}
	'''
	return {
		'messages': messages,
		'errors': errors,
	}
	
@register.inclusion_tag('snippits/show_field.html')
def show_field (field, extra_class = None, width = None):
	'''
	Format a form field in a standard way
	
	Uses Template: 'snippits/show_field.html'
	
	Tag Parameters:
		field: a form field to format
		css_class: a string with extra css classes
		width: a string with a valid CSS length
	
	Tag Definition: {% show_field field [css_class='' [width=auto]] %}
	Example: {% show_field form.notes 'half_height' '35em' %}
	'''
	return {
		'field': field,
		'extra_class': extra_class,
		'width': width,
	}

@register.simple_tag	
def spacer (width=1.2):
	'''
	Insert a horizontal spacer into the template.
	
	Uses Template: None
	
	Tag Parameters:
		width: a length measurment in em
	
	Tag Definition: {% spacer [width=1.2] %}
	Example: {% spacer 4 %}{# 4em horizontal spacer #}
	'''
	return '<div style="display: inline-block; width: %fem;"></div>' % width

@register.simple_tag	
def vspacer (height=1.2):
	'''
	Insert a vertical spacer into the template.
	
	Uses Template: None
	
	Tag Parameters: 
		width: a length measurement in em
	
	Tag Definition: {% vspacer [width=1.2] %}
	Example: {% vspacer 0.5 %} {# 0.5em vertical spacer #}
	'''
	return '<div style="display: inline-block; height: %fem;"></div>' % height

@register.tag
def content (parser, token):
	'''
	Wrap content to provide consistent styling.
	
	Uses Template: 'snippits/content.html'
	
	Tag Patameters:
		state: 'default' or 'error' or 'highlight' or 'background' or 'blank'
		width: a length measurement in em
		height: a length measurement in em
	
	Tag Definition; {% content [state='' [width=auto [height=auto]]] %}{% endcontent %}
	Example: {% content 'highlight' %}{{ messages }}{% endcontent %}
	'''
	tokens = token.split_contents()
	if len(tokens) > 4:
		raise template.TemplateSyntaxError, '%r tag takes at most two arguments'% tokens[0]
	state = None
	height = None
	width = None
	if len(tokens) > 1:
		state = tokens[1]
	if len(tokens) > 2:
		width = tokens[2]
	if len(tokens) > 3:
		height = tokens[3]
	nodelist = parser.parse(('endcontent',))
	parser.delete_first_token()
	
	if state and state[0] == state[-1] and state[0] in ('"', "'"):
		state = state[1:-1]
	if width and width[0] == width[-1] and width[0] in ('"', "'"):
		width = width[1:-1]
	if height and height[0] == height[-1] and height[0] in ('"', "'"):
		height = height[1:-1]
	return TemplateNode('snippits/content.html', nodelist, {
		'state': state,
		'width': width, 
		'height': height,
	})
	
@register.tag
def header (parser, token):
	'''
	Wrap content and style as a header.
	
	Uses Template: 'snippits/header.html'
	
	Tag Parameters: 
		root_link: 'on' to display the home link, 'off' to hide
	
	Tag Definition: {% header [root_link='on'] %}{% endheader #}
	Example: {% header %}{{ header_content }}{% endheader %}
	'''
	tokens = token.split_contents()
	root_link = True
	if len(tokens) > 2:
		raise template.TemplateSyntaxError, '%r tag takes at most one argument'% tokens[0]
	if len(tokens) > 1:
		if tokens[1] in ('"off"', "'off'"):
			root_link = False
	nodelist = parser.parse(('endheader',))
	parser.delete_first_token()
	return TemplateNode('snippits/header.html', nodelist, {'root_link': root_link})

@register.tag
def section (parser, token):
	'''
	Wrap content and style as a section with section title.
	
	Uses Template: 'snippits/section.html'
	
	Tag Parameters: 
		title: a string that is the section title
	
	Tag Definition: {% section title %}{% endsection #}
	Example: {% section 'Section Title' %}{{ content }}{% endsection %}
	'''
	try:
		tag, title = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, '%r tag requires a title' % tag
	nodelist = parser.parse(('endsection',))
	parser.delete_first_token()
	
	if title[0] == title[-1] and title[0] in ('"', "'"):
		title = title[1:-1]
	return TemplateNode('snippits/section.html', nodelist, {'section_title': title})
	
@register.tag
def data (parser, token):
	'''
	Wrap content and style as read-only data with an optional title.
	
	Uses Template: 'snippits/show_data.html'
	
	Tag Parameters: 
		title: a string that is the data title
	
	Tag Definition: {% data [title=''] %}{% enddata #}
	Example: {% data 'Some Awesome Data' %}{{ data }}{% enddata %}
	'''
	tokens = token.split_contents()
	title = None
	width = '33%'
	if len(tokens) > 1:
		title = tokens[1]
	if len(tokens) > 2:
		width = tokens[2]
	if len(tokens) > 3:
		raise template.TemplateSyntaxError, '%r tag takes at most two arguments'% tokens[0]
	nodelist = parser.parse(('enddata',))
	parser.delete_first_token()
	
	if title and title[0] == title[-1] and title[0] in ('"', "'"):
		title = title[1:-1]
	if width and width[0] == width[-1] and width[0] in ('"', "'"):
		width = width[1:-1]
	
	return TemplateNode('snippits/show_data.html', nodelist, {
		'data_title': title,
		'width': width
		})
	
class TemplateNode (template.Node):
	'''
	Renders templates for the following tag types: data, section, header and content
	'''
	def __init__ (self, template, nodelist= None, context=None):
		self.template = template
		self.nodelist = nodelist
		self.context = context if context else {}
		
	def render(self, context):
		t = template.loader.get_template(self.template)
		ctx = self.context
		if self.nodelist:
			contents = self.nodelist.render(context)
			ctx['contents'] = contents
		return t.render(template.Context(ctx, autoescape = context.autoescape))