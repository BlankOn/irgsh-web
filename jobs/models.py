from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Architecture(models.Model):
    architecture = models.CharField(max_length=6, primary_key=True)
    active = models.BooleanField()
    logical = models.BooleanField(default=False)

    def __unicode__(self):
        return self.architecture


class Distribution(models.Model):
    name = models.CharField("Distribution name", max_length=50, primary_key=True)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

class DistributionArchitecture(models.Model):
    name = models.ForeignKey('Distribution')
    architecture = models.ForeignKey(Architecture, limit_choices_to={'logical': False})
    active = models.BooleanField()

    def __unicode__(self):
        return self.name.name

    class Meta:
        unique_together = (("name", "architecture"),)

class Builder(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    architecture = models.ForeignKey(Architecture, limit_choices_to={'logical': False})
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

class BuilderAdministrator(models.Model):
    handler = models.ForeignKey(Builder)
    administrator = models.ForeignKey(User)
    
    class Meta:
        unique_together = (("handler", "administrator"),)

class Job(models.Model):

    JOB_STATES = (
        (u'N', u'New'),
        (u'S', u'Running'),
        (u'F', u'Failed'),
        (u'R', u'Restarted'),
        (u'C', u'Completed'),
        (u'X', u'Canceled'),
    )

    submitter = models.ForeignKey(User, editable=False)
    carbon_copy = models.TextField("Cc:", blank=True)
    submission_time = models.DateTimeField(default=datetime.now,editable=False)
    completion_time = models.DateTimeField(default=datetime.now,editable=False)
    state = models.CharField(max_length=1, choices=JOB_STATES, default=u'N', editable=False)
    distro = models.ForeignKey(Distribution)

    def __unicode__(self):
        return "%d: %s (%s): %s" % (self.id, self.submitter, self.distro, self.state)

class Task(models.Model):
    TASK_STATES = (
        (u'N', u'New'),
        (u'D', u'Downloading'),
        (u'R', u'Running'),
        (u'F', u'Failed'),
        (u'C', u'Completed'),
        (u'X', u'Canceled'),
    )

    JOB_VCS = (
        (u'none', 'None (tarball)'),
        (u'bzr', 'Bazaar'),
        (u'git', 'GIT'),
        (u'hg', 'Mercurial'),
    )

    job = models.ForeignKey(Job)
    state = models.CharField(max_length=1, choices=TASK_STATES, default=u'N', editable=False)
    debian_url = models.URLField("Package's URL", max_length=1024, verify_exists=False)
    debian_vcs = models.CharField("Package's VCS", max_length=10, choices=JOB_VCS)
    debian_tag = models.CharField("Package's Tag", max_length=50, blank=True)
    orig_url = models.URLField("Original source's URL", max_length=1024, blank=True)
    debian_copy = models.CharField(max_length=1024, editable=False)
    orig_copy = models.CharField(max_length=1024, editable=False)
    changelog = models.TextField(editable=False)

    class Meta:
        unique_together = (("job", "state","debian_url", "debian_vcs", "debian_tag", "orig_url"),)

class TaskManifest(models.Model):
    MANIFEST_TYPES = (
        (u'S', u'Source'),
        (u'B', u'Binary'),
    )
    task = models.ForeignKey(Task)
    name = models.CharField(max_length=120) 
    version = models.CharField(max_length=300)
    architecture = models.ForeignKey(Architecture)
    type = models.CharField(max_length=1, choices=MANIFEST_TYPES)

    class Meta:
        unique_together = (("name", "version","architecture", "type"),)
    

class TaskAssignment(models.Model):
    BUILDER_STATES = (
        (u'N', u'New'),
        (u'D', u'Downloading'),
        (u'P', u'Preparing environment'),
        (u'B', u'Building'),
        (u'U', u'Uploading'),
        (u'C', u'Completed'),
        (u'F', u'Failed'),
        (u'X', u'Canceled'),
    )
    task = models.ForeignKey(Task)
    assign_time = models.DateTimeField(default=datetime.now)
    start_time = models.DateTimeField()
    completion_time = models.DateTimeField()
    architecture = models.ForeignKey(Architecture)
    handler = models.ForeignKey(Builder)
    state = models.CharField(max_length=1, choices=BUILDER_STATES, default=u'N')

    class Meta:
        unique_together = (("task", "architecture","handler"),)
