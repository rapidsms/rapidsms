import rapidsms
from rapidsms.models import Msg 
from datetime import datetime, timedelta
from rapidsms.djangoproject.utils import * 
from django.contrib.auth.decorators import login_required, permission_required


def index(req):
    template_name="coretest/index.html"
    msg = Msg.objects.order_by('timestamp')
    all = []
    [ all.append(m) for m in msg ]
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.timestamp, x.timestamp))
    context = {}
    context['messages'] = msg
    return render_to_response(req, template_name, context )

