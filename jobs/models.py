from django.contrib.auth.models import User
from django.db import models

class Distribution(models.Model):
    name = models.CharField("Distribution name", max_length=50, primary_key=True)

    def __unicode__(self):
        return self.name

class Architecture(models.Model):
    architecture = models.CharField(max_length=6, primary_key=True)

    def __unicode__(self):
        return self.architecture

class Builder(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    location = models.CharField(max_length=100)
    architecture = models.ForeignKey(Architecture)

    def __unicode__(self):
        return self.name

class BuilderAdministrator(models.Model):
    handler = models.ForeignKey(Builder)
    administrator = models.ForeignKey(User)

class Job(models.Model):

    JOB_STATES = (
        (u'N', u'New'),
        (u'S', u'Started'),
        (u'B', u'Building'),
        (u'C', u'Completed'),
        (u'F', u'Failed'),
        (u'R', u'Restarted'),
        (u'U', u'Uploading to repository')
    )

    submitter = models.ForeignKey(User)
    submission_date = models.DateTimeField()
    completion_date = models.DateTimeField()
    state = models.CharField(max_length=1, choices=JOB_STATES, default=u'N')
    distro = models.ForeignKey(Distribution)

class Task(models.Model):
    JOB_VCS = (
        (u'none', 'None'),
        (u'bzr', 'Bazaar'),
        (u'git', 'GIT'),
        (u'hg', 'Mercurial'),
    )

    job = models.ForeignKey(Job)
    debian_url = models.URLField("Package's URL", max_length=1024, verify_exists=False)
    debian_vcs = models.CharField("Package's VCS", max_length=10, choices=JOB_VCS)
    debian_tag = models.CharField("Package's Tag", max_length=50)
    orig_url = models.URLField("Original source's URL", max_length=1024)


class JobBuilder(models.Model):
    BUILDER_STATES = (
        (u'N', u'New'),
        (u'D', u'Downloading'),
        (u'P', u'Preparing environment'),
        (u'B', u'Building'),
        (u'U', u'Uploading'),
        (u'C', u'Completed'),
        (u'F', u'Failed'),

    )
    task = models.ForeignKey(Task)
    architecture = models.ForeignKey(Architecture)
    handler = models.ForeignKey(Builder)
    state = models.CharField(max_length=1, choices=BUILDER_STATES, default=u'N')
