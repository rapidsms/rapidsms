from django import forms
from django.forms import widgets
from apps.httptester.models import Message

class MessageForm(forms.ModelForm):
    #phone_number = forms.CharField(max_length=15, label=u'Phone Number')
    body = forms.Textarea()
    class Meta:
        model = Message
        exclude = ("date", "outgoing", "phone_number")
        

