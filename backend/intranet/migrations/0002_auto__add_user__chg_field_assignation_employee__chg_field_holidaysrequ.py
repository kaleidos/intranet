# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Moving model 'User' to intranet
        db.rename_table('auth_user', 'intranet_user')
        db.add_column(u'intranet_user', 'is_company_team', self.gf('django.db.models.fields.BooleanField')(default=True)),
        db.add_column(u'intranet_user', 'raw_cost', self.gf('django.db.models.fields.FloatField')(default=10)),
        db.add_column(u'intranet_user', 'chargeability_cost', self.gf('django.db.models.fields.FloatField')(default=11)),
        db.add_column(u'intranet_user', 'profit_cost', self.gf('django.db.models.fields.FloatField')(default=12)),
        db.add_column(u'intranet_user', 'reset_password_token', self.gf('django.db.models.fields.CharField')(default=u'', max_length=40, blank=True)),
        db.send_create_signal(u'intranet', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'intranet_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'intranet.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'intranet_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'intranet.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])


        # Changing field 'Assignation.employee'
        db.alter_column(u'intranet_assignation', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intranet.User']))

        # Changing field 'HolidaysRequest.employee'
        db.alter_column(u'intranet_holidaysrequest', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intranet.User']))
        # Renaming field 'Project.kaleidos_id' to 'Project.internal_id'
        db.rename_column(u'intranet_project', 'kaleidos_id', 'internal_id')

        # Adding M2M table for field subscribers on 'Project'
        m2m_table_name = db.shorten_name(u'intranet_project_subscribers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'intranet.project'], null=False)),
            ('user', models.ForeignKey(orm[u'intranet.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])

        # Adding field 'Part.data'
        db.add_column(u'intranet_part', 'data',
                      self.gf('picklefield.fields.PickledObjectField')(default={}),
                      keep_default=False)

        # Adding M2M table for field projects on 'Part'
        m2m_table_name = db.shorten_name(u'intranet_part_projects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('part', models.ForeignKey(orm[u'intranet.part'], null=False)),
            ('project', models.ForeignKey(orm[u'intranet.project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['part_id', 'project_id'])


        # Changing field 'Part.employee'
        db.alter_column(u'intranet_part', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intranet.User']))
        # Renaming field 'Client.kaleidos_id' to 'Client.internal_id'
        db.rename_column(u'intranet_client', 'kaleidos_id', 'internal_id')

        # Changing field 'IntranetProfile.user'
        db.alter_column(u'intranet_intranetprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intranet.User']))

    def backwards(self, orm):
        # Moving model 'User' to auth
        db.delete_column(u'intranet_user', 'is_company_team'),
        db.delete_column(u'intranet_user', 'raw_cost'),
        db.delete_column(u'intranet_user', 'chargeability_cost'),
        db.delete_column(u'intranet_user', 'profit_cost'),
        db.delete_column(u'intranet_user', 'reset_password_token'),
        db.rename_table('intranet_user', 'auth_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'intranet_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'intranet_user_user_permissions'))


        # Changing field 'Assignation.employee'
        db.alter_column(u'intranet_assignation', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'HolidaysRequest.employee'
        db.alter_column(u'intranet_holidaysrequest', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Renaming field 'Project.internal_id' to 'Project.kaleidos_id'
        db.rename_column(u'intranet_project', 'internal_id', 'kaleidos_id')

        # Removing M2M table for field subscribers on 'Project'
        db.delete_table(db.shorten_name(u'intranet_project_subscribers'))

        # Deleting field 'Part.data'
        db.delete_column(u'intranet_part', 'data')

        # Removing M2M table for field projects on 'Part'
        db.delete_table(db.shorten_name(u'intranet_part_projects'))


        # Changing field 'Part.employee'
        db.alter_column(u'intranet_part', 'employee_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Renaming field 'Client.internal_id' to 'Client.kaleidos_id'
        db.rename_column(u'intranet_client', 'internal_id', 'kaleidos_id')


        # Changing field 'IntranetProfile.user'
        db.alter_column(u'intranet_intranetprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'intranet.assignation': {
            'Meta': {'unique_together': "(('employee', 'project'),)", 'object_name': 'Assignation'},
            'cost': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intranet.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intranet.Project']"})
        },
        u'intranet.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'contact_person': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'employees_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clients'", 'to': u"orm['intranet.Sector']"}),
            'ubication': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'})
        },
        u'intranet.holidaysrequest': {
            'Meta': {'object_name': 'HolidaysRequest'},
            'beginning': ('django.db.models.fields.DateField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holidays_requests'", 'to': u"orm['intranet.User']"}),
            'ending': ('django.db.models.fields.DateField', [], {}),
            'flexible_dates': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holidays_requests'", 'to': u"orm['intranet.HolidaysYear']"})
        },
        u'intranet.holidaysyear': {
            'Meta': {'object_name': 'HolidaysYear'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'intranet.imputation': {
            'Meta': {'ordering': "['part']", 'unique_together': "(('project', 'part'),)", 'object_name': 'Imputation'},
            'hours': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imputations'", 'to': u"orm['intranet.Part']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imputations'", 'to': u"orm['intranet.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'intranet.intranetprofile': {
            'Meta': {'unique_together': "(('user',),)", 'object_name': 'IntranetProfile'},
            'chargeability_cost': ('django.db.models.fields.FloatField', [], {'default': '11'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_kaleidos_team': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'profit_cost': ('django.db.models.fields.FloatField', [], {'default': '12'}),
            'raw_cost': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'intranet_profile'", 'to': u"orm['intranet.User']"})
        },
        u'intranet.invoice': {
            'Meta': {'ordering': "['estimated_through_date']", 'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['intranet.Client']"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'concept': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'estimated_perception_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'estimated_through_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'iva': ('django.db.models.fields.FloatField', [], {'default': '0.21'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'payment_conditions': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'perception_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'perception_state': ('django.db.models.fields.IntegerField', [], {'default': '-10'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['intranet.Project']"}),
            'quantity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'quantity_iva': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'through_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'intranet.part': {
            'Meta': {'ordering': "['-year', '-month']", 'unique_together': "(('month', 'year', 'employee'),)", 'object_name': 'Part'},
            'data': ('picklefield.fields.PickledObjectField', [], {'default': '{}'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': u"orm['intranet.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'parts'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['intranet.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'intranet.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project'", 'to': u"orm['intranet.Client']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'employees': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'default': 'None', 'to': u"orm['intranet.User']", 'through': u"orm['intranet.Assignation']", 'symmetrical': 'False', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'is_holidays': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_month_activity': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '600'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subscribed_projects'", 'default': 'None', 'to': u"orm['intranet.User']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'total_income': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'intranet.sector': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sector'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'intranet.specialday': {
            'Meta': {'ordering': "['date']", 'object_name': 'SpecialDay'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'intranet.user': {
            'Meta': {'object_name': 'User'},
            'chargeability_cost': ('django.db.models.fields.FloatField', [], {'default': '11'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_company_team': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'profit_cost': ('django.db.models.fields.FloatField', [], {'default': '12'}),
            'raw_cost': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'reset_password_token': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '40', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['intranet']
