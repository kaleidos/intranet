# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.template.defaultfilters import slugify


def slugify_uniquely(value, model, slugfield="slug"):
    """Returns a slug on a name which is unique within a model's table
       self.slug = SlugifyUniquely(self.name, self.__class__)
    """
    suffix = 0
    potential = base = slugify(value)
    if len(potential) == 0:
        potential = 'null'
    while True:
        if suffix:
                potential = "-".join([base, str(suffix)])
        if not model.objects.filter(**{slugfield: potential}).count():
                return potential
        # we hit a conflicting slug, so bump the suffix & try again
        suffix += 1


class Migration(DataMigration):
    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for part in orm.Part.objects.all():
            part.data = {}
            for imputation in part.imputations.all():
                project = imputation.project
                part.data[project.id] = {index+1: float(day_hours) for index, day_hours in enumerate(imputation.hours.split(','))}
                part.projects.add(project)
            part.save()

        for user in orm.User.objects.all():
            try:
                profile = orm.IntranetProfile.objects.get(user=user)
            except orm.IntranetProfile.DoesNotExist:
                profile = None

            if profile:
                user.is_company_team = profile.is_kaleidos_team
                user.raw_cost = profile.raw_cost
                user.chargeability_cost = profile.chargeability_cost
                user.profit_cost = profile.profit_cost

            user.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        for part in orm.Part.objects.all():
            for project_id, imputations in part.data.iteritems():
                try:
                    project = orm.Project.objects.get(pk=project_id)
                except orm.Project.DoesNotExist:
                    project = None

                if project:
                    imputations_list = [ (int(key), value) for key, value in imputations.iteritems() ]
                    imputations_list.sort()

                    orm.Imputation.objects.create(
                        slug=slugify_uniquely(u'%s-%s' % (unicode(project), unicode(part)), orm.Imputation),
                        part=part,
                        project=project,
                        hours=",".join([ unicode(imp[1] if imp[1] else 0) for imp in imputations_list ])
                    )
                    part.projects.add(project)
            part.save()

        for user in orm.User.objects.all():
            orm.IntranetProfile.objects.create(
                user=user,
                is_kaleidos_team=user.is_company_team,
                raw_cost=user.raw_cost,
                chargeability_cost=user.chargeability_cost,
                profit_cost=user.profit_cost,
            )

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
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
            'is_holidays': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'internal_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
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
    symmetrical = True
