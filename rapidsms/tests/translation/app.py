from django.utils import translation
from django.utils.translation import gettext as _

from rapidsms.apps.base import AppBase
from rapidsms.models import Connection
from rapidsms.router import send
from rapidsms.utils import translation as trans_helpers


class TranslationApp(AppBase):
    def handle(self, msg):
        if msg.text == "lang-hello":
            with translation.override(msg.connections[0].contact.language):
                msg.respond(_("hello"))
            return True
        elif msg.text == "settings-hello":
            msg.respond(_("hello"))
            return True


def lang_broadcast():
    connections = Connection.objects.all()
    for lang, conns in trans_helpers.group_connections(connections):
        with translation.override(lang):
            send(_("hello"), conns)
