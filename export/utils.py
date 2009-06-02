#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import http


def excel(data):
    def __table(t):
        return "<table>\n%s</table>" % "".join(map(__row, t))
    
    def __row(r):
        return "  <tr>\n%s  </tr>\n" % "".join(map(__col, r))
    
    def __col(c):
        return "    <td>%s</td>\n" % (c)
    
    # dump it as a simple html table
    html = __table(data)
    
    # download as an excel spreadsheet
    resp = http.HttpResponse(html, mimetype='application/vnd.ms-excel')
    resp["content-disposition"] = "attachment; filename=test.xls"
    return resp
