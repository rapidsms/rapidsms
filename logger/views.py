from rapidsms.webui.utils import render_to_response
from models import *
from datetime import datetime, timedelta
from utilities.export import export
from rapidsms.webui.utils import paginated

def index(req):
    template_name="logger/index.html"
    incoming = IncomingMessage.objects.order_by('received')
    outgoing = OutgoingMessage.objects.order_by('sent')
    all = []
    [ all.append(msg) for msg in incoming ]
    [ all.append(msg) for msg in outgoing]
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.date, x.date))
    context = {}
    context['messages'] = paginated(req, all, per_page=50)
    return render_to_response(req, template_name, context )

def csv_in(req, format='csv'):
    context = {}
    if req.user.is_authenticated():
        return export(IncomingMessage.objects.all())
    return export(IncomingMessage.objects.all(), ['id','text','backend','domain','received'])
    
def csv_out(req, format='csv'):
    context = {}
    if req.user.is_authenticated():
        return export(OutgoingMessage.objects.all())    
    return export(OutgoingMessage.objects.all(), ['id','text','backend','domain','sent'])
