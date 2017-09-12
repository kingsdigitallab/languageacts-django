# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0014_made_caption_optional'),
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
    ]
