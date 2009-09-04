#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, re
import datetime
from subprocess import *

from django import http
from django.db import models
from django.utils.text import capfirst
from django.core.exceptions import FieldError
from rapidsms.webui import settings


def database(req):
    """Returns a SQL dump of the current database, by reading the settings
       from the config file, and calling the relevant dump program. Currently,
       only mySQL and SQLite3 are supported."""
    
    conf = vars(settings)
    if settings.DATABASE_ENGINE == "mysql":
        cmd = "mysqldump --host=%(DATABASE_HOST)s --user=%(DATABASE_USER)s --password=%(DATABASE_USER)s %(DATABASE_NAME)s" % (conf)
    
    elif settings.DATABASE_ENGINE == "sqlite3":
        cmd = "sqlite3 %(DATABASE_NAME)s .dump" % (conf)
    
    else:
        return HttpResponse(
            "Sorry, %(DATABASE_ENGINE)s databases are not supported yet." % (conf),
            status=500, content_type="text/plain")
	
    # execute the dump command, and wait for it to terminate
    proc = Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    sql = proc.communicate()

    # download the file as plain text
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    resp = http.HttpResponse(sql, mimetype="text/plain")
    resp["content-disposition"] = "attachment; filename=%s.sql" % (today)
    return resp


def _get_model(app_label, model_name):
	model = models.get_model(app_label, model_name)
	
	# check that the model is valid
	if model is None:
		raise http.Http404(
		"App %r, model %r, not found."\
		% (app_label, model_name))
	
	return model


def str_to_excel(req):
    def __table(str):
        return "<table>\n%s</table>" % "".join(map(__row, str.split("\n")))
    
    def __row(str):
        return "  <tr>\n%s  </tr>\n" % "".join(map(__col, str.split("|")))
    
    def __col(str):
        str, cs = re.match("^(.*?)(?::(\d+)\s*)?$", str).groups()
        return "    <td colspan='%s'>%s</td>\n" % (cs, str)
    
    # dump it as a simple html table
    html = __table(req.POST["data"])
    
    # download as an excel spreadsheet
    resp = http.HttpResponse(html, mimetype='application/vnd.ms-excel')
    resp["content-disposition"] = "attachment; filename=test.xls"
    return resp


def model_to_excel(request, app_label, model_name, req_filters=None):
	model = _get_model(app_label, model_name)
	max_depth = 8
	rows = []
	
	# if no filters were explictly passed,
	# then we will look for them in the GET
	if req_filters is None:
		req_filters = request.GET
	
	# build a dict of filters, to control
	# which objects we get. todo: is this
	# dangerous? i can't see any way that
	# it is, but it seems kind of wrong
	filters = {}
	for k ,v in req_filters.items():
		filters[str(k)] = v
	
	# fetch the data (might raise if any of the
	# params couldn't be matched to model fields
	try:
		export_data = model.objects.filter(**filters)
	
	except FieldError, e:
		return http.HttpResponse(e.message,
		status=500, mimetype="text/plain")
	
	# sort the records if requested
	if "sort" in req_filters:
		export_data = export_data.order_by(str(req_filters["sort"]))
	
	
	# this function builds a flat list of column titles (verbose names)
	# recursively, to include as much data as possible in the export
	def build_header(model, depth=0, prefix=""):
		columns = []
		
		for field in model._meta.fields:
			caption = prefix + capfirst(field.verbose_name)
			
			# if this field is a foreign key, then
			# we will recurse to fetch it's fields
			if (hasattr(field, "rel")) and (field.rel is not None) and (depth < max_depth):
				columns.extend(build_header(field.rel.to, depth+1, caption + ": "))
				
			# not a foreign key, so append
			# this column in it's raw form
			else:
				columns.append("<th>%s</th>" % (caption))
		
		return columns
	
	
	# the first row contains no data, just field names
	rows.append("<tr>%s</tr>" % ("".join(build_header(model))))
	
	
	# this function is *way* too similar to the function
	# above to warrant its independance. abstraction!
	def build_row(model, instance=None, depth=0):
		columns = []
		
		for field in model._meta.fields:
			
			# fetch the value of this cell
			if instance is not None:
				cell = getattr(instance, field.name)
			
			# the cell is NONE, but we'll still need to
			# recurse if it's a foreign key, so the row
			# doesn't end up shorter the rest
			else: cell = None
			
			
			# if this field is a foreign key, then
			# we will recurse to fetch it's fields
			if (hasattr(field, "rel")) and (field.rel is not None) and (depth < max_depth):
				columns.extend(build_row(field.rel.to, cell, depth+1))
			
			# if this cell is none, insert a blank column,
			# so we don't have "None" all over the place
			elif (cell is None):
				columns.append("<td></td>")
			
			# not a foreign key, so append
			# this column in it's raw form
			else: columns.append("<td>%s</td>" % (cell))
		return columns
	
	
	# the matrix of dumped data
	for object in export_data:
		row = "".join(build_row(model, object))
		rows.append("<tr>%s</tr>" % (row))
	
	
	# dump it as a simple html table
	html = "<table>%s</table>" % ("\n".join(rows))
	
	# download as an excel spreadsheet
	resp = http.HttpResponse(html, mimetype='application/vnd.ms-excel')
	resp["content-disposition"] = "attachment; filename=%s.xls" % model_name
	return resp
