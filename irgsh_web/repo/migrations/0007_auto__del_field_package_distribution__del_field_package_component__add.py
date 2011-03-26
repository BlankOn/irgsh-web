# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Package', fields ['distribution', 'name']
        db.delete_unique('repo_package', ['distribution_id', 'name'])

        # Deleting field 'Package.distribution'
        db.delete_column('repo_package', 'distribution_id')

        # Deleting field 'Package.component'
        db.delete_column('repo_package', 'component_id')

        # Adding unique constraint on 'Package', fields ['name']
        db.create_unique('repo_package', ['name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Package', fields ['name']
        db.delete_unique('repo_package', ['name'])

        # User chose to not deal with backwards NULL issues for 'Package.distribution'
        raise RuntimeError("Cannot reverse this migration. 'Package.distribution' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Package.component'
        raise RuntimeError("Cannot reverse this migration. 'Package.component' and its values cannot be restored.")

        # Adding unique constraint on 'Package', fields ['distribution', 'name']
        db.create_unique('repo_package', ['distribution_id', 'name'])


    models = {
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

    complete_apps = ['repo']
