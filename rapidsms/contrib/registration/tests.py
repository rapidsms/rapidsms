
from rapidsms.tests.scripted import TestScript


class TestRegister(TestScript):

    def testRegister(self):
        self.assertInteraction("""
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
        """)

    def testLang(self):
        self.assertInteraction("""
          8005551212 > lang english
          8005551212 < %s
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
          8005551212 > lang english
          8005551212 < I will speak to you in English.
          8005551212 > lang klingon
          8005551212 < Sorry, I don't speak "klingon".
        """ % ("You must JOIN or IDENTIFY yourself before you can set " +
               "your language preference."))

    def testHelp(self):
        self.assertInteraction("""
          8005551212 > lang
          8005551212 < To set your language, send LANGUAGE <CODE>
          8005551212 > register
          8005551212 < To register, send JOIN <NAME>
        """)
