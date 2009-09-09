import re
#import rapidsms
#from rapidsms.parsers import Matcher
from models import *

#class App(rapidsms.App):
   
def Testing(alias,code,fn,ln,langfield):
    if alias is not None and code is None :
	rep = Reporter(
	    first_name=fn, last_name=ln,
	    alias=alias, registered_self=True)
        rep.save()
    else:
        rep = Reporter.objects.get(alias__iexact=code) #not sure about syntax.
        rep.language = langfield 
        rep.save()
	    
Testing("34873","42358",None,None,"fr")
