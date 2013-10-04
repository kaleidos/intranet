# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'auth.User'
        db.create_table(u'auth_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'auth', ['User'])

        # Adding model 'IntranetProfile'
        db.create_table('intranet_intranetprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='intranet_profile', to=orm['auth.User'])),
            ('is_kaleidos_team', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('raw_cost', self.gf('django.db.models.fields.FloatField')(default=10)),
            ('chargeability_cost', self.gf('django.db.models.fields.FloatField')(default=11)),
            ('profit_cost', self.gf('django.db.models.fields.FloatField')(default=12)),
        ))
        db.send_create_signal('intranet', ['IntranetProfile'])

        # Adding unique constraint on 'IntranetProfile', fields ['user']
        db.create_unique('intranet_intranetprofile', ['user_id'])

        # Adding model 'Assignation'
        db.create_table('intranet_assignation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intranet.Project'])),
            ('cost', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('intranet', ['Assignation'])

        # Adding unique constraint on 'Assignation', fields ['employee', 'project']
        db.create_unique('intranet_assignation', ['employee_id', 'project_id'])

        # Adding model 'Project'
        db.create_table('intranet_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('kaleidos_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=600)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='project', to=orm['intranet.Client'])),
            ('total_income', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('is_holidays', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_month_activity', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('intranet', ['Project'])

        # Adding model 'Part'
        db.create_table('intranet_part', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('month', self.gf('django.db.models.fields.IntegerField')()),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parts', to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('intranet', ['Part'])

        # Adding unique constraint on 'Part', fields ['month', 'year', 'employee']
        db.create_unique('intranet_part', ['month', 'year', 'employee_id'])

        # Adding model 'Imputation'
        db.create_table('intranet_imputation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='imputations', to=orm['intranet.Project'])),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(related_name='imputations', to=orm['intranet.Part'])),
            ('hours', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=500)),
        ))
        db.send_create_signal('intranet', ['Imputation'])

        # Adding unique constraint on 'Imputation', fields ['project', 'part']
        db.create_unique('intranet_imputation', ['project_id', 'part_id'])

        # Adding model 'SpecialDay'
        db.create_table('intranet_specialday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('intranet', ['SpecialDay'])

        # Adding model 'Sector'
        db.create_table('intranet_sector', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('intranet', ['Sector'])

        # Adding model 'Client'
        db.create_table('intranet_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kaleidos_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(related_name='clients', to=orm['intranet.Sector'])),
            ('employees_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('contact_person', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('ubication', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('intranet', ['Client'])

        # Adding model 'Invoice'
        db.create_table('intranet_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('perception_state', self.gf('django.db.models.fields.IntegerField')(default=-10)),
            ('quantity', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('quantity_iva', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('iva', self.gf('django.db.models.fields.FloatField')(default=0.18)),
            ('concept', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('payment_conditions', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('payment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['intranet.Client'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['intranet.Project'])),
            ('estimated_through_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('through_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('estimated_perception_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('perception_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('invoice_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('intranet', ['Invoice'])

        # Adding model 'HolidaysYear'
        db.create_table('intranet_holidaysyear', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('intranet', ['HolidaysYear'])

        # Adding model 'HolidaysRequest'
        db.create_table('intranet_holidaysrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='holidays_requests', to=orm['auth.User'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(related_name='holidays_requests', to=orm['intranet.HolidaysYear'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('beginning', self.gf('django.db.models.fields.DateField')()),
            ('ending', self.gf('django.db.models.fields.DateField')()),
            ('flexible_dates', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comments', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('intranet', ['HolidaysRequest'])


    def backwards(self, orm):
        # Removing unique constraint on 'Imputation', fields ['project', 'part']
        db.delete_unique('intranet_imputation', ['project_id', 'part_id'])

        # Removing unique constraint on 'Part', fields ['month', 'year', 'employee']
        db.delete_unique('intranet_part', ['month', 'year', 'employee_id'])

        # Removing unique constraint on 'Assignation', fields ['employee', 'project']
        db.delete_unique('intranet_assignation', ['employee_id', 'project_id'])

        # Removing unique constraint on 'IntranetProfile', fields ['user']
        db.delete_unique('intranet_intranetprofile', ['user_id'])

        # Deleting model 'IntranetProfile'
        db.delete_table('intranet_intranetprofile')

        # Deleting model 'Assignation'
        db.delete_table('intranet_assignation')

        # Deleting model 'Project'
        db.delete_table('intranet_project')

        # Deleting model 'Part'
        db.delete_table('intranet_part')

        # Deleting model 'Imputation'
        db.delete_table('intranet_imputation')

        # Deleting model 'SpecialDay'
        db.delete_table('intranet_specialday')

        # Deleting model 'Sector'
        db.delete_table('intranet_sector')

        # Deleting model 'Client'
        db.delete_table('intranet_client')

        # Deleting model 'Invoice'
        db.delete_table('intranet_invoice')

        # Deleting model 'HolidaysYear'
        db.delete_table('intranet_holidaysyear')

        # Deleting model 'HolidaysRequest'
        db.delete_table('intranet_holidaysrequest')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'intranet.assignation': {
            'Meta': {'unique_together': "(('employee', 'project'),)", 'object_name': 'Assignation'},
            'cost': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['intranet.Project']"})
        },
        'intranet.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'contact_person': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'employees_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kaleidos_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clients'", 'to': "orm['intranet.Sector']"}),
            'ubication': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'})
        },
        'intranet.holidaysrequest': {
            'Meta': {'object_name': 'HolidaysRequest'},
            'beginning': ('django.db.models.fields.DateField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holidays_requests'", 'to': "orm['auth.User']"}),
            'ending': ('django.db.models.fields.DateField', [], {}),
            'flexible_dates': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holidays_requests'", 'to': "orm['intranet.HolidaysYear']"})
        },
        'intranet.holidaysyear': {
            'Meta': {'object_name': 'HolidaysYear'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'intranet.imputation': {
            'Meta': {'ordering': "['part']", 'unique_together': "(('project', 'part'),)", 'object_name': 'Imputation'},
            'hours': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imputations'", 'to': "orm['intranet.Part']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imputations'", 'to': "orm['intranet.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        'intranet.intranetprofile': {
            'Meta': {'unique_together': "(('user',),)", 'object_name': 'IntranetProfile'},
            'chargeability_cost': ('django.db.models.fields.FloatField', [], {'default': '11'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_kaleidos_team': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'profit_cost': ('django.db.models.fields.FloatField', [], {'default': '12'}),
            'raw_cost': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'intranet_profile'", 'to': "orm['auth.User']"})
        },
        'intranet.invoice': {
            'Meta': {'ordering': "['estimated_through_date']", 'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['intranet.Client']"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'concept': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'estimated_perception_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'estimated_through_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'iva': ('django.db.models.fields.FloatField', [], {'default': '0.18'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'payment_conditions': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'perception_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'perception_state': ('django.db.models.fields.IntegerField', [], {'default': '-10'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['intranet.Project']"}),
            'quantity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'quantity_iva': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'through_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'intranet.part': {
            'Meta': {'ordering': "['-year', '-month']", 'unique_together': "(('month', 'year', 'employee'),)", 'object_name': 'Part'},
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'intranet.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project'", 'to': "orm['intranet.Client']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'employees': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'default': 'None', 'to': "orm['auth.User']", 'through': "orm['intranet.Assignation']", 'symmetrical': 'False', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_holidays': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kaleidos_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'last_month_activity': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '600'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'total_income': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'intranet.sector': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sector'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'intranet.specialday': {
            'Meta': {'ordering': "['date']", 'object_name': 'SpecialDay'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['intranet']
