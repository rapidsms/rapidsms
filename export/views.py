#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from django.http import HttpResponse

def json_xls(req):
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
    resp = HttpResponse(html, mimetype='application/vnd.ms-excel')
    resp["content-disposition"] = "attachment; filename=test.xls"
    return resp
