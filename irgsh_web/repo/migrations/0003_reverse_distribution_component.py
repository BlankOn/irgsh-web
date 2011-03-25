# encoding: utf-8
import datetime
from collections import defaultdict

from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        mapping = defaultdict(list)
        for component in orm.Component.objects.all():
            mapping[component.distribution].append(component)

        for dist, components in mapping.items():
            for component in components:
                dist.components.add(component)

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration")

    models = {
        'repo.architecture': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Architecture'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'repo.component': {
            'Meta': {'ordering': "('distribution', 'name')", 'unique_together': "(('name', 'distribution'),)", 'object_name': 'Component'},
            'distribution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Distribution']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'repo.distribution': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Distribution'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'architectures': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['repo.Architecture']", 'symmetrical': 'False'}),
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'component_list'", 'symmetrical': 'False', 'to': "orm['repo.Component']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'repo.package': {
            'Meta': {'ordering': "('component__distribution__name', 'component__name', 'name')", 'unique_together': "(('name', 'distribution'),)", 'object_name': 'Package'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Component']"}),
            'distribution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Distribution']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['repo']
