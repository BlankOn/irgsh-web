from datetime import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User

from picklefield.fields import PickledObjectField

from irgsh_web.repo.models import Distribution as RepoDistribution
from irgsh_web.repo.models import Package as RepoPackage
from irgsh_web.repo.models import Architecture

SOURCE = 0
BINARY = 1

TARBALL = 'tarball'
BZR = 'bzr'

SPECIFICATION_STATUS = (
    ( -2, _('Rejected')),
    ( -1, _('Failed')),
    (100, _('Waiting for initialization')),
    (101, _('Downloading source file')),
    (102, _('Downloading orig file')),
    (103, _('Distributed')),
    (104, _('Source uploaded')),
    (200, _('Building repository')),
    (999, _('Finished')),
)

BUILD_TASK_STATUS = (
    ( -2, _('Cancelled')),
    ( -1, _('Failed')),
    (  0, _('Waiting for builder')),
    (100, _('Preparing builder')),
    (101, _('Downloading source file')),
    (102, _('Downloading orig file')),
    (103, _('Building package')),
    (104, _('Package built')),
    (201, _('Uploading package')),
    (202, _('Package uploaded')),
    (999, _('Finished')),
)

PACKAGE_CONTENT_TYPE = (
    (SOURCE, _('Source')),
    (BINARY, _('Binary')),
)

SOURCE_TYPE = (
    (TARBALL, _('Tarball')),
    (BZR, _('Bazaar')),
)

class Distribution(models.Model):
    '''
    List of distributions, e.g. ombilin, ombilin-updates, pattimura, etc
    '''
    repo = models.ForeignKey(RepoDistribution, unique=True)
    active = models.BooleanField(default=True)

    mirror = models.CharField(max_length=255,
                              help_text=_('e.g. http://arsip.blankonlinux.or.id/blankon/'))
    dist = models.CharField(max_length=50,
                            help_text=_('e.g. ombilin, pattimura, etc'))
    components = models.CharField(max_length=255,
                                  help_text=_('e.g. main universe. Separate multiple components by a space'))
    extra = models.TextField(blank=True, default='',
                             verbose_name=_('Additional repositories'),
                             help_text=_('Use sources.list syntax'))

    def __unicode__(self):
        return unicode(self.name())

    def name(self):
        return self.repo.name

class Builder(models.Model):
    '''
    List of package builders
    '''
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, default=None, blank=True)

    architecture = models.ForeignKey(Architecture)
    location = models.CharField(max_length=255, null=True, default=None,
                                blank=True)
    remark = models.TextField(default='', blank=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.architecture)

class Specification(models.Model):
    '''
    List of submitted package specifications
    '''
    distribution = models.ForeignKey(Distribution)
    submitter = models.ForeignKey(User)
    status = models.IntegerField(choices=SPECIFICATION_STATUS, default=0)

    source = models.CharField(max_length=1024)
    orig = models.CharField(max_length=1024, null=True, default=None,
                            blank=True)
    source_type = models.CharField(max_length=25, choices=SOURCE_TYPE)
    source_opts = PickledObjectField(null=True, default=None)

    package = models.ForeignKey(RepoPackage, null=True, default=None)
    version = models.CharField(max_length=255, null=True, default=None)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        param = {'dist': self.distribution}
        if self.package is None:
            return _('Unknown package (%(dist)s)') % param
        else:
            param.update({'package': self.package})
            return _('%(package)s (%(dist)s)') % param

    def dsc(self):
        if self.package is None:
            return None
        return '%s_%s.dsc' % (self.package, self.version.split(':')[-1])

    def add_log(self, message):
        log = SpecificationLog(spec=self)
        log.log = message
        log.save()
        return log

class SpecificationResource(models.Model):
    '''
    List of files needed by a specification
    '''
    specification = models.ForeignKey(Specification, unique=True)

    source_name = models.CharField(max_length=1024, null=True, default=None)
    source_started = models.DateTimeField(null=True, default=None)
    source_finished = models.DateTimeField(null=True, default=None)

    orig_name = models.CharField(max_length=1024, null=True, default=None)
    orig_started = models.DateTimeField(null=True, default=None)
    orig_finished = models.DateTimeField(null=True, default=None)

class Installation(models.Model):
    package = models.ForeignKey(RepoPackage, unique=True)
    specification = models.ForeignKey(Specification)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

class Package(models.Model):
    '''
    List of packages described in debian/control file
    '''
    specification = models.ForeignKey(Specification, related_name='content')
    name = models.CharField(max_length=1024)
    architecture = models.CharField(max_length=255)
    type = models.IntegerField(choices=PACKAGE_CONTENT_TYPE)
    description = models.CharField(max_length=1025, null=True, default=None)
    long_description = models.TextField(null=True, default=None)

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
    builder = models.ForeignKey(Builder, null=True, default=None)

    status = models.IntegerField(choices=BUILD_TASK_STATUS, default=0)
    build_log = models.DateTimeField(null=True, default=None)

    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('specification', 'architecture',)

    def __unicode__(self):
        return '%s (%s)' % (self.task_id, self.id)

    def add_log(self, message):
        log = BuildTaskLog(task=self)
        log.log = message
        log.save()
        return log

    def changes(self):
        if self.specification.package is None:
            return None
        return '%s_%s_%s.changes' % (self.specification.package,
                                     self.specification.version,
                                     self.architecture.name)

    def upload_path(self):
        return str(self.architecture.name)

class BuildTaskLog(models.Model):
    '''
    List of messages (including status change) sent by builders during
    building a package
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

class SpecificationLog(models.Model):
    spec = models.ForeignKey(Specification)
    log = models.TextField()

    created = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        if len(self.log) > 50:
            return '%s...' % self.log[:50]
        else:
            return self.log

