# Generated by Django 2.2.13 on 2020-06-24 13:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cms', '0048_strand_blog_news_contextual_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogGuestAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=512)),
            ],
        ),
        migrations.AddField(
            model_name='blogpost',
            name='guest_author',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='cms.BlogGuestAuthor',
                verbose_name='Guest Post'
            ),
        ),
    ]
