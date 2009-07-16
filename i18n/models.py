from django.db import models
from patterns.models import Pattern

# some really bare bones models for localization
class Language(models.Model):
    pattern = models.ForeignKey(Pattern)
    name = models.CharField(max_length = 50) # e.g. "English"

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.pattern.name)

class Translation(models.Model):
    language = models.ForeignKey(Language)
    
    # The actual original (probably english) string will be 
    # used as the key into the other languages.  This is 
    # similar to the python/django _() i18n support.  
    original = models.TextField()
    translation = models.TextField()

    def __unicode__(self):
        return "%s --> %s (%s)" % (self.original, self.translation, self.language.name)
