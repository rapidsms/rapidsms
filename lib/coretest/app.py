!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms


class App(rapidsms.App):

    def handle(self, msg):
        try:
            Msg.objects.create(connection=self.connection,text=msg.text,datetime=msg.date)
        except Exception as err:
            Msg.objects.create(text="error:%s %s" % (self.connection.identity,err,msg.text),datetime=msg.date)


