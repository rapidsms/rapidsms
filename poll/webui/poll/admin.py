from django.contrib import admin 
from webui.poll.models import *

admin.site.register(Respondant)
admin.site.register(Message)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Entry)

