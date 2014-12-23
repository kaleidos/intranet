# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.id_card'
        db.add_column(u'intranet_user', 'id_card',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'User.color'
        db.add_column(u'intranet_user', 'color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=7, blank=True),
                      keep_default=False)

        # Adding field 'User.twitter_account'
        db.add_column(u'intranet_user', 'twitter_account',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'User.mobile'
        db.add_column(u'intranet_user', 'mobile',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=12, blank=True),
                      keep_default=False)

        # Adding field 'User.phone'
        db.add_column(u'intranet_user', 'phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=12, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'User.id_card'
        db.delete_column(u'intranet_user', 'id_card')

        # Deleting field 'User.color'
        db.delete_column(u'intranet_user', 'color')

        # Deleting field 'User.twitter_account'
        db.delete_column(u'intranet_user', 'twitter_account')

        # Deleting field 'User.mobile'
        db.delete_column(u'intranet_user', 'mobile')

        # Deleting field 'User.phone'
        db.delete_column(u'intranet_user', 'phone')


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
            'flexible_dates': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        u'intranet.quote': {
            'Meta': {'ordering': "['-created_date']", 'object_name': 'Quote'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'quotes_created'", 'null': 'True', 'to': u"orm['intranet.User']"}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'quotes'", 'null': 'True', 'to': u"orm['intranet.User']"}),
            'explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'external_author': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quote': ('django.db.models.fields.TextField', [], {}),
            'users_rates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'quotes_rated'", 'default': 'None', 'to': u"orm['intranet.User']", 'through': u"orm['intranet.QuoteScore']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'intranet.quotescore': {
            'Meta': {'unique_together': "(('user', 'quote'),)", 'object_name': 'QuoteScore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quote': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scores'", 'to': u"orm['intranet.Quote']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quote_scores'", 'to': u"orm['intranet.User']"})
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
        u'intranet.talk': {
            'Meta': {'object_name': 'Talk'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'place': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'talkers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'talks_offers'", 'default': 'None', 'to': u"orm['intranet.User']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'talkers_are_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wanters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'talks_wanted'", 'default': 'None', 'to': u"orm['intranet.User']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'intranet.user': {
            'Meta': {'object_name': 'User'},
            'chargeability_cost': ('django.db.models.fields.FloatField', [], {'default': '11'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_card': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_company_team': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'profit_cost': ('django.db.models.fields.FloatField', [], {'default': '12'}),
            'raw_cost': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'reset_password_token': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '40', 'blank': 'True'}),
            'twitter_account': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['intranet']