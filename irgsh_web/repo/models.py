from django.db import models
from django.utils.translation import ugettext as _

class Architecture(models.Model):
    '''
    List of architectures
    '''
    name = models.CharField(max_length=10, unique=True,
                            help_text=_('e.g. i386, amd64'))
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Component(models.Model):
    '''
    List of components
    '''
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Distribution(models.Model):
    '''
    List of distributions
    '''
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    architectures = models.ManyToManyField(Architecture)
    components = models.ManyToManyField(Component)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Package(models.Model):
    '''
    List of (source) packages
    '''
    name = models.CharField(max_length=1024)
    distribution = models.ForeignKey(Distribution)
    component = models.ForeignKey(Component)

    class Meta:
        unique_together = ('name', 'distribution',)
        ordering = ('component__distribution__name', 'component__name', 'name',)

    def __unicode__(self):
        return '%s/%s/%s' % (self.name, self.component.distribution.name, self.component.name)

