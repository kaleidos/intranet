#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from intranet.models import *
from django.db import connection

import datetime

class Command(BaseCommand):
    args = ''
    help = 'Migrate data to new version'

    # handle
    def handle(self, *args, **options):
        #Adding hstore data

#        add_data_sql = """
#        BEGIN;
#        -- Application: intranet
#        -- Model: Part
#        ALTER TABLE "intranet_part"
#            ADD "data" text;
#        ALTER TABLE "intranet_part"
#            ALTER COLUMN "data" SET NOT NULL;
#        -- Table: intranet_part_projects
#
#        -- DROP TABLE intranet_part_projects;
#
#        CREATE TABLE intranet_part_projects
#        (
#          id serial NOT NULL,
#          part_id integer NOT NULL,
#          project_id integer NOT NULL,
#          CONSTRAINT intranet_part_projects_pkey PRIMARY KEY (id),
#          CONSTRAINT intranet_part_projects_project_id_fkey FOREIGN KEY (project_id)
#              REFERENCES intranet_project (id) MATCH SIMPLE
#              ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
#          CONSTRAINT part_id_refs_id_5bd118d6 FOREIGN KEY (part_id)
#              REFERENCES intranet_part (id) MATCH SIMPLE
#              ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
#          CONSTRAINT intranet_part_projects_part_id_project_id_key UNIQUE (part_id, project_id)
#        )
#        WITH (
#          OIDS=FALSE
#        );
#        ALTER TABLE intranet_part_projects
#          OWNER TO intranet;
#
#        -- Index: intranet_part_projects_part_id
#
#        -- DROP INDEX intranet_part_projects_part_id;
#
#        CREATE INDEX intranet_part_projects_part_id
#          ON intranet_part_projects
#          USING btree
#          (part_id);
#
#        -- Index: intranet_part_projects_project_id
#
#        -- DROP INDEX intranet_part_projects_project_id;
#
#        CREATE INDEX intranet_part_projects_project_id
#          ON intranet_part_projects
#          USING btree
#          (project_id);
#
#        COMMIT;
#        """
#        cursor = connection.cursor()
#        cursor.execute(add_data_sql)

        #Migrating old data
        for part in Part.objects.all():
            part.data = {}
            for imputation in part.imputations.all():
                project = imputation.project
                part.data[project.id] = {index+1: float(day_hours) for index, day_hours in enumerate(imputation.hours.split(','))}

            print part.data
            part.save()


#        for project in Project.objects.all():
#            for part in Part.objects.all():
#                print project, part, part.total_hours(project.id)
#                part.calendar_frame()
