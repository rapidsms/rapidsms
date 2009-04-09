#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.parsers.keyworder import * 

from models import *
from utils import *

class App(rapidsms.app.App):

    # lets use the Keyworder parser!
    kw = Keyworder()

    def start(self):
        self.separator = "[,\.\s]*"
	self.leading_pattern = "[\"'\s]*"
	self.trailing_pattern = "[\.,\"'\s]*"
        self.report_pattern = None 
        self.supplies_reports_tokens = []
	self.setup()

    def parse(self, message):
        self.handled = False

    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    self.debug("HANDLE")
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                    # short-circuit handler calls because 
                    # we are responding to this message
                    return self.handled 
                except TypeError:
                    # TODO only except NoneType error
                    # nothing was found, use default handler
                    self.debug("NO MATCH")
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception, e:
            self.error(e) 


    def outgoing(self, message):
        pass 

    def __get(self, model, **kwargs):
            try:
                    # attempt to fetch the object
                    return model.objects.get(**kwargs)
            
            # no objects or multiple objects found (in the latter case,
            # something is probably broken, so perhaps we should warn)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                    return None

    def __identify(self, message, task=None):
            reporter = self.__get(Reporter, connection=message.connection)
            
            # if the caller is not identified, then send
            # them a message asking them to do so, and
            # stop further processing
            if not reporter:
                    msg = "Please register your mobile number"
                    if task: msg += " before %s" % (task)
                    msg += ", by replying: I AM <USERNAME>"
                    message.respond(msg)
		    self.handled = True
            
            return reporter 

    # HELP----------------------------------------------------------
    @kw("help")
    def help(self, message):
        message.respond("HELP!")
	self.handled = True
    

    # ALERT <NOTICE> ----------------------------------------------------------
    kw.prefix = "alert"

    @kw("(whatever)")
    def alert(self, message, notice):
            reporter = self.__identify(message.connection, "alerting")
            Notification.objects.create(reporter=reporter, notice=notice)
            message.respond("Thanks, %s. Your supervisor has been alerted." % (reporter.first_name))
	    self.handled = True

    # SUBMIT A REPORT--------------------------------------------------------

    #kw.prefix = ""
    # TODO figure out how to use the auto-generated regex
    #@kw("[\"'\s]*(letters)[,\.\s]*(letters)[,\.\s]*(\w+|\d+)(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?[\.,\"'\s]*")
    #@kw("(report_pattern)")
    def report(self, message, code, type, *data): 
        self.debug("MATCH")
        #reporter = self.__identify(message.connection, "reporting")
	handled = False
	for supply in self.supplies_reports_tokens:
	    try:
	        # gather list of report dicts for this supply code
	        reports = supply[code.upper()]
	        self.debug("SUPPLY MATCH")
		for report in reports:
		    try:
			# gather list of token tuples for this report type
		        tokens = report[type.upper()]
			self.debug("REPORT MATCH")
			info = []
			for t, d in zip(tokens, data):
			    # gather info for confirmation message, matching
			    # abbreviations from the token tuple to the received data
			    info.append("%s=%s" % (t[0], d or "??"))

			# assemble and send response
			message.respond("Received report for %s %s: %s.\nIf this is not correct, reply with CANCEL" %\
			    (code.upper(), type.upper(), ", ".join(info)))
			# keep track of whether we have responded so we send only one 'Oops' message
			self.handled = True
			break

		    except KeyError:
		        continue	

		if not self.handled:
		    message.respond("Oops. Cannot find a report called %s for %s. Available reports for %s are %s" %\
		        (type.upper(), code.upper(), code.upper(), ", ".join([r.keys().pop().upper() for r in reports]))) 
		    self.handled = True
		    break

	    except KeyError:
	        continue
		#if not handled:
		#    message.respond("Oops. Cannot find a supply called %s. Available supplies are %s" %\
		#	(code.upper(), ", ".join([s.keys().pop().upper() for s in self.supplies_reports_tokens]))) 


    def setup(self):
        # create a list of dictionaries mapping supplies to lists of their
        # reports, which are dictionaries mapping report types to a list
        # of their tokens, as tuples of token.abbr, token.regex
        # e.g.,
        # [    
        #      {supply_code : 
        #          [
        #          {report_type : [(token.abbr, token.regex),...]},
        #          ...
        #          ]
        #       },
        #       ...
        # ]
        # 
        #supplies_reports_tokens = []
        supplies = Supply.objects.all()
        for s in supplies:
            # gather reports for this supply
            reports = s.report_set.all()
            reports_tokens = []
            for r in reports:
                # gather tokens for this report as a list of tuples
                tokens = r.token_set.order_by('sequence').\
                            values_list('abbreviation','regex')
                # make a dictionary mapping this report type to its token list
                # and add the dict to the running report_tokens list
                reports_tokens.append(dict([(r.type.upper(),tokens)]))
            # make a dictionary mapping this supply code to its report list
            # and add the dict to the running supply_report_tokens list
            self.supplies_reports_tokens.append(dict([(s.code.upper(), reports_tokens)]))
        self.debug(self.supplies_reports_tokens)

        # lists for keeping track of supply codes, report types, and 
        # number of tokens for use generating ranges
        supply_code_lengths = []
        report_code_lengths = []
        number_of_tokens = []
        # list for keeping track token sequences
        sequence_tokens = []
        for supply_reports_tokens in self.supplies_reports_tokens:
            for supply_code,reports in supply_reports_tokens.iteritems():
                # add the length of the supply code to our list
                self.debug("len(supply_code)=%s" % (len(supply_code)))
                supply_code_lengths.append(len(supply_code))
                for report in reports:
                    for report_type, tokens in report.iteritems():
                        # add the length of the report type to our list
                        self.debug("len(report_type)=%s len(tokens)=%s" % (len(report_type), len(tokens)))
                        report_code_lengths.append(len(report_type))
                        # add the number of tokens for this report to our list
                        number_of_tokens.append(len(tokens))
                        for i, token in enumerate(tokens):
                            # add a tuple of token's sequence and pattern to our list
                            sequence_tokens.append((i, token[1]))
                            self.debug((i, token[1]))

        # list for final patterns for each sequence
        pattern_for_sequences = []
        # iterate up to the maximum number of tokens (longest report)
        number_of_tokens.sort()
        for n in range(number_of_tokens[-1]):
            # gather all tokens that are at this sequence
            # (all tokens that are the third token in a report, for example)
            def tokens_at_sequence(t): return t[0] == n
            patterns_at_sequence = filter(tokens_at_sequence, sequence_tokens)
            self.debug(patterns_at_sequence)
            # gather the unique patterns out of these tokens and create a
            # regex for all of them (by adding an or between them all)
            #
            # let me break it down, starting from the inside:
            # do a list comprehension to get the pattern from the second 
            # position in the tuple, then limit to unique patterns, then
            # join the patterns together with a pipe between each one, and
            # finally add the resulting pattern to the list
            unique_patterns = '|'.join(unique(map((lambda t: t[1]),patterns_at_sequence)))
            self.debug("PATTERNS")
            self.debug(unique_patterns)
	    # fix any patterns we just or-ed together so they are the kind of or we want
	    # e.g., (\w+)|(\d+) => (\w+|\d+)
            pattern_for_sequences.append(unique_patterns.replace(')|(', '|'))
        self.debug(pattern_for_sequences)

        # create a pattern for supply_code that matches any word as long as
        # the shortest code and no longer than the longest code
        supply_code_lengths.sort()
        #TODO this only captures the last character if the range is {4,4}
        #supply_code_pattern = '(\w){%s,%s}' % (supply_code_lengths[0], supply_code_lengths[-1])
        #supply_code_pattern = '(letters)'
        supply_code_pattern = '([a-z]+)'
        self.debug(supply_code_pattern)
        # create a pattern for report type that matches any word as long as
        # the shortest code and no longer than the longest code
        report_code_lengths.sort()
        #report_code_pattern = '(\w){%s,%s}' % (report_code_lengths[0], report_code_lengths[-1])
        #report_code_pattern = '(letters)'
        report_code_pattern = '([a-z]+)'
        self.debug(report_code_pattern)
        # wrap all of the sequence patterns (except for the first one) 
	# with separators and make them optional.
	# this way all possible reports (that have at least one token)
	# will be matched, but we are able to capture n tokens
	#
	# i wonder whether doing a list comprehension or 
        # mapping a lambda is faster here
        #wrapped_patterns = ['(?:[,\.\s]*%s)?' % (p) for p in pattern_for_sequences]
        wrapped_patterns = map((lambda p: '(?:[,\.\s]*%s)?' % (p)),pattern_for_sequences[1:]) 
        self.debug(wrapped_patterns)
        # put all the patterns together!
        self.report_pattern = self.leading_pattern + supply_code_pattern +\
            self.separator + report_code_pattern + self.separator + pattern_for_sequences[0] + ''.join(wrapped_patterns) + self.trailing_pattern
	# hack into keyworder parser in an attempt to make this work
        #self.kw.TOKEN_MAP.append(('report_pattern', str('(' + self.report_pattern + ')')))
	self.kw.regexen.append((re.compile(self.report_pattern, re.IGNORECASE), getattr(self,'report').im_func))
        #self.debug(Keyworder.TOKEN_MAP)
        self.debug(self.report_pattern)
