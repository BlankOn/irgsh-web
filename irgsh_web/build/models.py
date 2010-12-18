from datetime import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User

from picklefield.fields import PickledObjectField

SOURCE_PACKAGE = 0
BINARY_PACKAGE = 1

TARBALL = 0
BZR = 1

BUILD_TASK_STATUS = (
    (-1, _('Failed')),
    (0, _('Unknown')),
    (1, _('Specification received')),
    (2, _('Downloading source file')),
    (3, _('Downloading orig file')),
    (4, _('Building package')),
)

PACKAGE_CONTENT_TYPE = (
    (SOURCE_PACKAGE, _('Source')),
    (BINARY_PACKAGE, _('Binary')),
)

ORIG_TYPE = (
    (TARBALL, _('Tarball')),
    (BZR, _('Bazaar')),
)

class Architecture(models.Model):
    '''
    List of supported architectures
    '''
    name = models.CharField(max_length=10, unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class Distribution(models.Model):
    '''
    List of distributions, e.g. ombilin, ombilin-updates, pattimura, etc
    '''
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    mirror = models.CharField(max_length=255)
    dist = models.CharField(max_length=50)
    components = models.CharField(max_length=255)
    extra = models.TextField(blank=True, default='')

    def __unicode__(self):
        return self.name

class Builder(models.Model):
    '''
    List of package builders
    '''
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, default=None)

    architecture = models.ForeignKey(Architecture)
    location = models.CharField(max_length=255, null=True)
    remark = models.TextField(null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.architecture)

class SourcePackage(models.Model):
    '''
    List of source packages
    '''
    name = models.CharField(max_length=255)
    distribution = models.ForeignKey(Distribution)

    class Meta:
        unique_together = ('name', 'distribution',)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.distribution)

class Specification(models.Model):
    '''
    List of submitted package specifications
    '''
    distribution = models.ForeignKey(Distribution)
    submitter = models.ForeignKey(User)

    source = models.CharField(max_length=255)
    orig = models.CharField(max_length=255, null=True, default=None)
    source_type = models.IntegerField(choices=ORIG_TYPE, null=True, default=None)
    source_opts = PickledObjectField(null=True, default=None)
    
    source_package = models.ForeignKey(SourcePackage, null=True, default=None)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        param = {'distribution': self.distribution}
        if self.package is None:
            return _('Unknown package (%(dist)s)') % param
        else:
            param.update({'package': self.package})
            return _('%(package)s (%(dist)s)') % param

class Package(models.Model):
    '''
    List of packages described in debian/control file
    '''
    specification = models.ForeignKey(Specification)
    name = models.CharField(max_length=255)
    architecture = models.CharField(null=True, default=None, max_length=50)
    type = models.IntegerField(choices=PACKAGE_CONTENT_TYPE)

    created = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('specification', 'name', 'architecture', 'type',)

    def __unicode__(self):
        param = {'package': self.name, 'arch': self.architecture}
        if self.type == SOURCE_PACKAGE:
            return _('%(package)s (source)') % param
        else:
            return _('%(package)s (%(arch)s)') % param
    
class BuildTask(models.Model):
    '''
    List of tasks assigned to package builders
    '''
    specification = models.ForeignKey(Specification)
    architecture = models.ForeignKey(Architecture)

    task_id = models.CharField(max_length=255) # celery task_id
    status = models.IntegerField(choices=BUILD_TASK_STATUS, default=0)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('specification', 'architecture',)

    def __unicode__(self):
        return '%s (%s)' % (self.task_id, self.id)

class BuildTaskLog(models.Model):
    '''
    List of logs sent by package bulders during building packages
    '''
    task = models.ForeignKey(BuildTask)
    log = models.TextField()
    
    created = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        if len(self.log) > 50:
            return '%s...' % self.log[:50]
        else:
            return self.log

