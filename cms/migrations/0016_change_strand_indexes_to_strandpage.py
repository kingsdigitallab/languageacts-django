# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType
from cms.models import HomePage, IndexPage, StrandPage
import modelcluster 

def swap_types(apps, schema_editor):
    # Define our content types
    index_ct = ContentType.objects.get_for_model(IndexPage)
    strand_ct = ContentType.objects.get_for_model(StrandPage)

    # Find the homepage and its indexpage children
    homepage = HomePage.objects.first()
    if homepage:
        index_pages = homepage.get_children().filter(content_type=index_ct).exclude(title__icontains='about')

        for p in index_pages.all():
            children = p.get_children()

            sp = StrandPage()
            sp.title = p.title
            sp.specific.body = p.specific.body
            sp.parent = HomePage
            sp.slug = "temp"
            sp.path = '0'
            sp.depth = '0'
            sp.save()
            sp.slug = p.slug

            for child in children.all():
                c.parent = sp
                c.save()

            sp.path = p.path
            sp.depth = p.depth

            p.delete()
            sp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_strandpage'),
    ]

    operations = [
        migrations.RunPython(swap_types),
        migrations.AddField(
            model_name='indexpage',
            name='strands',
            field=models.ManyToManyField(to='cms.StrandPage'),
        ),
        migrations.AlterField(
            model_name='indexpage',
            name='strands',
            field=models.ManyToManyField(blank=True, to='cms.StrandPage'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='strands',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='cms.StrandPage'),
        ),
        migrations.AddField(
            model_name='event',
            name='strands',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='cms.StrandPage'),
        ),
        migrations.AddField(
            model_name='newspost',
            name='strands',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='cms.StrandPage'),
        ),
        migrations.AlterField(
            model_name='indexpage',
            name='strands',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='cms.StrandPage'),
        ),
    ]
