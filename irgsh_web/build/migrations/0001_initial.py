# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Distribution'
        db.create_table('build_distribution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Distribution'], unique=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('mirror', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dist', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('components', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('extra', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('build', ['Distribution'])

        # Adding model 'Worker'
        db.create_table('build_worker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_activity', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('cert_subject', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1024)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('ssh_public_key', self.gf('django.db.models.fields.CharField')(default=None, max_length=2048, null=True, blank=True)),
        ))
        db.send_create_signal('build', ['Worker'])

        # Adding model 'Builder'
        db.create_table('build_builder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_activity', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('cert_subject', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1024)),
            ('architecture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Architecture'])),
            ('location', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
            ('ssh_public_key', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('remark', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('build', ['Builder'])

        # Adding model 'Specification'
        db.create_table('build_specification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('distribution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.Distribution'])),
            ('submitter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('orig', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024, null=True, blank=True)),
            ('source_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('source_opts_raw', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('source_opts', self.gf('picklefield.fields.PickledObjectField')(default=None, null=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['repo.Package'], null=True)),
            ('version', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
            ('changelog', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('source_uploaded', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('finished', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal('build', ['Specification'])

        # Adding model 'SpecificationResource'
        db.create_table('build_specificationresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.Specification'], unique=True)),
            ('source_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024, null=True)),
            ('source_started', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('source_finished', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('orig_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=1024, null=True)),
            ('orig_started', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('orig_finished', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal('build', ['SpecificationResource'])

        # Adding model 'Installation'
        db.create_table('build_installation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Package'], unique=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.Specification'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('build', ['Installation'])

        # Adding model 'Package'
        db.create_table('build_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content', to=orm['build.Specification'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('architecture', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(default=None, max_length=1025, null=True)),
            ('long_description', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('build', ['Package'])

        # Adding unique constraint on 'Package', fields ['specification', 'name', 'architecture', 'type']
        db.create_unique('build_package', ['specification_id', 'name', 'architecture', 'type'])

        # Adding model 'BuildTask'
        db.create_table('build_buildtask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.Specification'])),
            ('architecture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repo.Architecture'])),
            ('task_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('builder', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['build.Builder'], null=True)),
            ('assigned', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('build_log', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('changes', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('finished', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal('build', ['BuildTask'])

        # Adding unique constraint on 'BuildTask', fields ['specification', 'architecture']
        db.create_unique('build_buildtask', ['specification_id', 'architecture_id'])

        # Adding model 'BuildTaskLog'
        db.create_table('build_buildtasklog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.BuildTask'])),
            ('log', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('build', ['BuildTaskLog'])

        # Adding model 'SpecificationLog'
        db.create_table('build_specificationlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spec', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['build.Specification'])),
            ('log', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('build', ['SpecificationLog'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'BuildTask', fields ['specification', 'architecture']
        db.delete_unique('build_buildtask', ['specification_id', 'architecture_id'])

        # Removing unique constraint on 'Package', fields ['specification', 'name', 'architecture', 'type']
        db.delete_unique('build_package', ['specification_id', 'name', 'architecture', 'type'])

        # Deleting model 'Distribution'
        db.delete_table('build_distribution')

        # Deleting model 'Worker'
        db.delete_table('build_worker')

        # Deleting model 'Builder'
        db.delete_table('build_builder')

        # Deleting model 'Specification'
        db.delete_table('build_specification')

        # Deleting model 'SpecificationResource'
        db.delete_table('build_specificationresource')

        # Deleting model 'Installation'
        db.delete_table('build_installation')

        # Deleting model 'Package'
        db.delete_table('build_package')

        # Deleting model 'BuildTask'
        db.delete_table('build_buildtask')

        # Deleting model 'BuildTaskLog'
        db.delete_table('build_buildtasklog')

        # Deleting model 'SpecificationLog'
        db.delete_table('build_specificationlog')


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
        'build.installation': {
            'Meta': {'object_name': 'Installation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repo.Package']", 'unique': 'True'}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.Specification']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        'build.specificationresource': {
            'Meta': {'object_name': 'SpecificationResource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orig_finished': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'orig_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1024', 'null': 'True'}),
            'orig_started': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'source_finished': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'source_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1024', 'null': 'True'}),
            'source_started': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['build.Specification']", 'unique': 'True'})
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

    complete_apps = ['build']
