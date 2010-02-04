#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils import render_to_response


def dashboard(req):
	return render_to_response(req, "dashboard.html")
