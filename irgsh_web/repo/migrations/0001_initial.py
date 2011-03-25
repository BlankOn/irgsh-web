# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Architecture'
        db.create_table('repo_architecture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('repo', ['Architecture'])

        # Adding model 'Distribution'
        db.create_table('repo_distribution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('repo', ['Distribution'])

        # Adding M2M table for field architectures on 'Distribution'
        db.create_table('repo_distribution_architectures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('distribution', models.ForeignKey(orm['repo.distribution'], null=False)),
            ('architecture', models.ForeignKey(orm['repo.architecture'], null=False))
        ))
        db.create_unique('repo_distribution_architectures', ['distribution_id', 'architecture_id'])

        # Adding model 'Component'
        db.create_table('repo_component', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('distribution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Distribution'])),
        ))
        db.send_create_signal('repo', ['Component'])

        # Adding unique constraint on 'Component', fields ['name', 'distribution']
        db.create_unique('repo_component', ['name', 'distribution_id'])

        # Adding model 'Package'
        db.create_table('repo_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('distribution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Distribution'])),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Component'])),
        ))
        db.send_create_signal('repo', ['Package'])

        # Adding unique constraint on 'Package', fields ['name', 'distribution']
        db.create_unique('repo_package', ['name', 'distribution_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Package', fields ['name', 'distribution']
        db.delete_unique('repo_package', ['name', 'distribution_id'])

        # Removing unique constraint on 'Component', fields ['name', 'distribution']
        db.delete_unique('repo_component', ['name', 'distribution_id'])

        # Deleting model 'Architecture'
        db.delete_table('repo_architecture')

        # Deleting model 'Distribution'
        db.delete_table('repo_distribution')

        # Removing M2M table for field architectures on 'Distribution'
        db.delete_table('repo_distribution_architectures')

        # Deleting model 'Component'
        db.delete_table('repo_component')

        # Deleting model 'Package'
        db.delete_table('repo_package')


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
