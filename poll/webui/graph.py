#!/usr/bin/env python
# vim: noet

import os, sys
from random import choice
from datetime import datetime, date, timedelta
from pygooglechart import SimpleLineChart, Axis, PieChart2D, StackedVerticalBarChart

from poll.models import *

# craziness to get the graphs to save in the right spot
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))

# path, from above craziness, to graphs directory
GRAPH_DIR = 'webui/graphs/'

# graph sizes to generate (small & big)
GRAPH_SIZES = ['240', '500']


def golden(width):
	return int(width/1.6180339887498948482)


def graph_entries(q):
	#question = get_object_or_404(Question, pk=q.pk)
	question = Question.objects.get(pk=q.pk)

	# generate question participation graph
	# turned off since we're not displaying
	#print graph_participation(q)

	# figure out what kind of question we have
	# and generate the appropriate graph
	if question.type == 'M':
		return graph_multiple_choice(question)
	if question.type == 'B':
		return graph_boolean(question)
	if question.type == 'F':
		return graph_free_text(question)


def graph_participation(q):
	#question = get_object_or_404(Question, pk=q.pk)
	question = Question.objects.get(pk=q.pk)

	# grab ALL entries for this question
	entries = Entry.objects.filter(question=question)

	# look up how many people were asked this question
	# and make a ratio
	# if None, use 0
	if question.sent_to:
		participation = float(len(entries))/float(question.sent_to)
	else: 
		participation = 0.0

	# normalize data
	pending = 100 * (1.0 - participation)
	participants = 100 - pending 

	for size in GRAPH_SIZES:
		# configure and save the graph
		pie = PieChart2D(int(size), golden(int(size)))
		pie.add_data([pending, participants])
		pie.set_legend(['Pending' , 'Respondants'])
		pie.set_colours(['0091C7','0FBBD0'])
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-participation.png'
		pie.download(filename)
		print 'saved ' + filename

	return 'graphed participation ' + question.text


def graph_multiple_choice(q):
	#question = get_object_or_404(Question, pk=q.pk)
	question = Question.objects.get(pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question).order_by('choice')

	# old code for handling any number of choices
	# choices = { " " : 0 }
	# choices = choices.fromkeys(xrange(len(answers)), 0)

	# hardcode of four choices since ui limits to four
	choices = { 1 : 0, 2 : 0, 3 : 0, 4 : 0 }
	
	# grab the parsed entries for this question
	entries = Entry.objects.filter(question=question,\
					is_unparseable=False)

	# i'm assuming here that the Entry.text is the
	# same thing as the Answer.choice, presumably
	# a number for each choice 1 through  n
	# 
	# iterate entries and tally the choices
	for e in entries:
		if int(e.text) in choices:
			choices[int(e.text)] += 1

	choice_counts = sortedDictValues1(choices)

	# collect the long, textual representation
	# of the answer choice for labelling the graph
	# along with the choice counts of each choice
	# for display on large graphs
	long_answers_big = []
	long_answers_small = []
	for a in answers:
		long_answers_small.append(a.text)
		long_answers_big.append(a.text + ' (' + str(choices[int(a.choice)]) + ')' )

	
	for size in GRAPH_SIZES:
		# configure and save the graph
		bar = StackedVerticalBarChart(int(size), golden(int(size)),\
					y_range=(0, max(choice_counts)))
		bar.set_colours([choice(['0091C7','0FBBD0'])])
		bar.add_data(choice_counts)
		bar.set_bar_width(int(int(size)/(len(choices)+1)))
		if (size == GRAPH_SIZES[0]):
			index = bar.set_axis_labels(Axis.BOTTOM, long_answers_small)
		else:
			index = bar.set_axis_labels(Axis.BOTTOM, long_answers_big)
		bar.set_axis_style(index, '202020', font_size=9, alignment=0)
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-entries.png'
		bar.download(filename)
		print 'saved ' + filename
	
	return 'graphed entries ' + question.text


def sortedDictValues1(adict):
	items = adict.items()
	items.sort()
	return [value for key, value in items]


def graph_boolean(q):
	# this method is not very DRY with respect to
	# graph_multiple_choice
	# will probably combine these once we figure
	# out how they will be used

	#question = get_object_or_404(Question, pk=q.pk)
	question = Question.objects.get(pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question)

	# only two choices unless we accept maybies
	choices = { 0 : 0, 1 : 0 }

	# grab the parsed entries for this question
	entries = Entry.objects.filter(question=question,\
					is_unparseable=False)

	# i'm assuming here that the Entry.text is the
	# same thing as the Answer.choice, presumably
	# 0 for false/no and 1 for true/yes
	# 
	# iterate entries and tally the choices
	for e in entries:
		if int(e.text) in choices:
			choices[int(e.text)] += 1
	
	# collect the long, textual representation
	# of the answer choice for labelling the graph
	# along with the choice counts of each choice
	# for display on large graphs
	long_answers_big = []
	long_answers_small = []
	for a in answers:
		long_answers_small.append(a.text)
		long_answers_big.append(a.text + ' (' + str(choices[int(a.choice)]) + ')' )

	for size in GRAPH_SIZES:
		# configure and save the graph
		pie = PieChart2D(int(size), golden(int(size)))
		# TODO normalize values
		pie.add_data(choices.values())
		if (size == GRAPH_SIZES[0]):
			pie.set_legend(long_answers_small)
		else:
			pie.set_legend(long_answers_big)
		pie.set_colours(['0091C7','0FBBD0'])
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-entries.png'
		pie.download(filename)
		print 'saved ' + filename
	
	return 'graphed entries ' + question.text


def graph_free_text(q):
	return 'called graph_free_text'
