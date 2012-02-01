from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    twitter = models.SlugField(null=True, default=None, blank=True,
                               help_text=_('Twitter username without @ (at sign)'))

    def clean(self):
        if self.twitter is not None:
            self.twitter = self.twitter.strip()
            if self.twitter.startswith('@'):
                self.twitter = self.twitter[1:]
            elif self.twitter == '':
                self.twitter = None

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

