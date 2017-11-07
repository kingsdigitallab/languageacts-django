# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType
from cms.models import HomePage, TagResults
import modelcluster 
import django.db.models.deletion

def create_page(apps, schema_editor):
    # Find the homepage and create a tagged-pages subpage
    homepage = HomePage.objects.first()
    if homepage:
        p = TagResults()
        p.title = 'Tagged Pages'
        p.slug= 'tagged-pages'

        homepage.add_child(instance=p)

class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0020_tagresults'),
    ]

    operations = [
        migrations.RunPython(create_page),
    ]
