# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType
from cms.models import HomePage, IndexPage, StrandPage
import modelcluster 
import django.db.models.deletion

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
            sp.slug = "strand_{}".format(p.slug)

            homepage.add_child(instance=sp)

            for c in children.all():
                c.move(sp, pos='last-child')

            p.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_image_grid'),
    ]

    operations = [
        migrations.CreateModel(
            name='StrandPage',
            fields=[
                ('indexpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cms.IndexPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.indexpage', models.Model),
        ),
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
        migrations.RunPython(swap_types),
    ]
