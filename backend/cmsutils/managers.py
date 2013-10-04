# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models

class ActiveManager(models.Manager):
    """
    This special manager only retrieves active objects (when the current date
    is between the object's publish date and/or its expiration date).

    The date fields can be given when creating the Manager instance, and by
    default are "publish_date" and "expire_date". If either is None then
    the manager will not take it into account for filtering.

    Example definition for a model:

    class ExampleModel(models.Model):
        publish_date = models.DateTimeField()
        expire_date = models.DateTimeField(blank=True, null=True)

        actives = ActiveManager(from_date='publish_date', to_date='expire_date')

    Or if the model only had an expire_date:

    class ExampleModel(models.Model):
        expire_date = models.DateTimeField(blank=True, null=True)

        actives = ActiveManager(from_date=None, to_date='expire_date')

    The manager has an attribute ActiveManager.date_filters which can be used
    in custom queries. For example, if you have a ManyToMany relationship to a
    model with ActiveManager and you can't access via the manager (because you
    need to use select_related) then you can do:

    instance.many_to_many.filter(*ManyToManyModel.actives.date_filters)

    """

    def __init__(self, from_date='publish_date', to_date='expire_date'):
        super(ActiveManager, self).__init__()
        self.from_date = from_date
        self.to_date = to_date
        now = datetime.now
        if from_date and to_date:
            self.date_filters = (models.Q(**{'%s__isnull' % self.to_date: True}) |
                                 models.Q(**{'%s__gte' % self.to_date:now}),
                                 models.Q(**{'%s__isnull' % self.from_date: True}) |
                                 models.Q(**{'%s__lte' % self.from_date: now}))

        elif from_date:
            self.date_filters = (models.Q(**{'%s__isnull' % self.from_date: True}) |
                                 models.Q(**{'%s__lte' % self.from_date: now}),)
        elif to_date:
            self.date_filters = (models.Q(**{'%s__isnull' % self.to_date: True}) |
                                 models.Q(**{'%s__gte' % self.to_date: now}),)
        else:
            raise ValueError, "At least one date field is required"

    def actives(self):
        """Retrieves items with publication dates according to self.date_filters
        """
        return super(ActiveManager, self).all().filter(*self.date_filters)


class OrderedManager(models.Manager):
    """
    Simple manager that retrieves objects ordered by "position" field
    """

    def get_query_set(self):
        """Retrieves items with publication dates according to self.date_filters
        """
        return super(OrderedManager, self).get_query_set().order_by('position')
