# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-23 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_blog_page_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='date',
            field=models.DateField(),
        ),
    ]