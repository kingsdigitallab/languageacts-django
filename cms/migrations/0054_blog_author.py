# Generated by Django 2.2.13 on 2020-06-25 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0053_auto_20200625_1453'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BlogGuestAuthor',
            new_name='BlogAuthor',
        ),
    ]
