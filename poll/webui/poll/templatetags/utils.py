from django.template import Library
from poll.models import *
register = Library()

# for date_selector
from django.utils.dates import MONTHS
import time

# INCLUSION TAGS --------------------------------------------

@register.inclusion_tag("partials/date-selector.html")
def date_selector(prefix):
	now = time.localtime()
	
	return {
		"prefix": prefix,
		"days":   list((d, d==now.tm_mday) for d in range(1, 32)),
		"months": list((unicode(MONTHS[m]), m==now.tm_mon) for m in MONTHS.iterkeys()),
		"years":  list((y, y==now.tm_year) for y in range(now.tm_year, now.tm_year+5))
	}


@register.inclusion_tag("partials/question-summary.html")
def question_summary(question):
	return { "question" : question }


@register.inclusion_tag("partials/question-full.html")
def question_full(question):
	return { "question" : question }


@register.inclusion_tag("partials/add-answer.html")
def add_answer(number):
	return { "questions" : Question.objects.all(),\
				"number" : number }

# SIMPLE TAGS -----------------------------------------------

@register.simple_tag
def num_unparseables():
	num = len(Entry.objects.filter(is_unparseable=True))
	if num > 0: return "(%d)" % num
	else:       return ""
