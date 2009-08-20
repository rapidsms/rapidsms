from rapidsms.webui.utils import render_to_response
from models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required("logger.can_view")
def index(req):
    template_name="logger/index.html"
    incoming = IncomingMessage.objects.order_by('received')
    outgoing = OutgoingMessage.objects.order_by('sent')
    all = []
    [ all.append(msg) for msg in incoming ]
    [ all.append(msg) for msg in outgoing]
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.date, x.date))
    return render_to_response(req, template_name, { "messages": all})

