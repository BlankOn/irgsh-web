# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.db.models import Q

class Migration(DataMigration):

    def forwards(self, orm):
        for Model in [orm.Specification, orm.BuildTask]:
            items = Model.objects.filter(Q(status=999) | Q(status__lt=0)) \
                                 .filter(finished=None)

            timestamps = {}
            for item in items:
                timestamps[item.id] = item.updated

            for item_id, finished in timestamps.items():
                Model.objects.filter(pk=item_id).update(finished=finished)

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration")

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'build.builder': {
            'Meta': {'ordering': "('-active', 'name')", 'object_name': 'Builder'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'architecture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Architecture']"}),
            'cert_subject': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_activity': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'remark': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'ssh_public_key': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        'build.buildtask': {
            'Meta': {'ordering': "('-created',)", 'unique_together': "(('specification', 'architecture'),)", 'object_name': 'BuildTask'},
            'architecture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Architecture']"}),
            'assigned': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'build_log': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'builder': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['build.Builder']", 'null': 'True'}),
            'changes': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'finished': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.Specification']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'build.buildtasklog': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'BuildTaskLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.BuildTask']"})
        },
        'build.distribution': {
            'Meta': {'object_name': 'Distribution'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'components': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dist': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mirror': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Distribution']", 'unique': 'True'})
        },
        'build.package': {
            'Meta': {'unique_together': "(('specification', 'name', 'architecture', 'type'),)", 'object_name': 'Package'},
            'architecture': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1025', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content'", 'to': "orm['build.Specification']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'build.specification': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Specification'},
            'changelog': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'distribution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.Distribution']"}),
            'finished': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orig': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['repo.Package']", 'null': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'source_opts': ('picklefield.fields.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'source_opts_raw': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'source_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'source_uploaded': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'})
        },
        'build.specificationlog': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'SpecificationLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {}),
            'spec': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.Specification']"})
        },
        'build.worker': {
            'Meta': {'object_name': 'Worker'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cert_subject': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_activity': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'ssh_public_key': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'repo.architecture': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Architecture'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'repo.component': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Component'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'repo.distribution': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Distribution'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'architectures': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['repo.Architecture']", 'symmetrical': 'False'}),
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['repo.Component']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'repo.package': {
            'Meta': {'object_name': 'Package'},
            'distribution': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['repo.Distribution']", 'through': "orm['repo.PackageDistribution']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        },
        'repo.packagedistribution': {
            'Meta': {'unique_together': "(('package', 'distribution'),)", 'object_name': 'PackageDistribution'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Component']"}),
            'distribution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Distribution']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Package']"})
        }
    }

    complete_apps = ['build']
