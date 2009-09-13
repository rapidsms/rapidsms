from django.template import Library
from poll.models import *
register = Library()

# UTIL -----------------------------------------------------

def rand():
	from random import randint
	return randint(111111,999999)

# INCLUSION TAGS --------------------------------------------

from django.utils.dates import MONTHS
import datetime, time

@register.inclusion_tag("poll/partials/date-selector.html")
def date_selector(prefix, date=None, disabled=False):
	
	# if no date was provided, select TODAY
	if date == None:
		t = time.localtime()
	
	# if a date was provided (such as a Question.start
	# or .end), extract the values to prepopulate <select>s
	elif isinstance(date, datetime.date):
		t = date.timetuple()
	
	# we have no idea what was passed
	else: raise Exception("wat")

	return {
		"prefix": prefix,
		"disabled": disabled,
		
		# for hidden fields
		"year":   t.tm_year,
		"month":  t.tm_mon,
		"day":    t.tm_mday,
		
		# for drop-down selects
		"days":   list((d, d==t.tm_mday) for d in range(1, 32)),
		"months": list((unicode(MONTHS[m]), m==t.tm_mon) for m in MONTHS.iterkeys()),
		"years":  list((y, y==t.tm_year) for y in range(t.tm_year, t.tm_year+5))
	}


def question_data(question):
	from django.utils import simplejson
	data = [(answer.text, votes) for answer, votes in question.results()]
	return { "question" : question, "rnd": rand(), "data": simplejson.dumps(data) }

@register.inclusion_tag("poll/partials/question-summary.html")
def question_summary(question):
	return question_data(question) 


@register.inclusion_tag("poll/partials/question-full.html")
def question_full(question):
	return question_data(question)


@register.inclusion_tag("poll/partials/add-answer.html")
def add_answer(number):
	return { "questions" : Question.objects.all(),\
				"number" : number }

# SIMPLE TAGS -----------------------------------------------

@register.simple_tag
def num_unparseables():
	num = len(Entry.objects.filter(is_unparseable=True))
	if num > 0: return "(%d)" % num
	else:       return ""
