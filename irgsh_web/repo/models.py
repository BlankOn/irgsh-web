from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

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
    name = models.CharField(max_length=1024, unique=True)
    distribution = models.ManyToManyField(Distribution, through='PackageDistribution')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('package_show', args=[self.name])

class PackageDistribution(models.Model):
    package = models.ForeignKey(Package)
    distribution = models.ForeignKey(Distribution)
    component = models.ForeignKey(Component)

    class Meta:
        unique_together = ('package', 'distribution',)

    def clean(self):
        relation = self.distribution.components.filter(pk=self.component.id)
        if len(relation) == 0:
            raise ValidationError('Distribution %s does not have %s component' % \
                                  (self.distribution, self.component))

    def __unicode__(self):
        return '%s (%s)' % (self.distribution, self.component)

