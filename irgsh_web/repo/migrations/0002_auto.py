# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field components on 'Distribution'
        db.create_table('repo_distribution_components', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('distribution', models.ForeignKey(orm['repo.distribution'], null=False)),
            ('component', models.ForeignKey(orm['repo.component'], null=False))
        ))
        db.create_unique('repo_distribution_components', ['distribution_id', 'component_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field components on 'Distribution'
        db.delete_table('repo_distribution_components')


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
