# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-28 11:43
from __future__ import unicode_literals

import cms.models.streamfield
from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks
import wagtail.wagtailembeds.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('wagtailcore', '0040_page_draft_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'pullquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock()), (b'affiliation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'style', cms.models.streamfield.PullQuoteStyleChoiceBlock())], icon='openquote')), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.RichTextBlock()), (b'alignment', cms.models.streamfield.ImageFormatChoiceBlock())], icon='image', label='Aligned image')), (b'document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse')), (b'link', wagtail.wagtailcore.blocks.StructBlock([(b'url', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock(required=False)), (b'label', wagtail.wagtailcore.blocks.CharBlock()), (b'style', cms.models.streamfield.LinkStyleChoiceBlock())], icon='link')), (b'embed', wagtail.wagtailembeds.blocks.EmbedBlock(icon='media')), (b'html', wagtail.wagtailcore.blocks.StructBlock([(b'html', wagtail.wagtailcore.blocks.RawHTMLBlock()), (b'alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())], icon='code', label='Raw HTML'))])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='IndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'pullquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock()), (b'affiliation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'style', cms.models.streamfield.PullQuoteStyleChoiceBlock())], icon='openquote')), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.RichTextBlock()), (b'alignment', cms.models.streamfield.ImageFormatChoiceBlock())], icon='image', label='Aligned image')), (b'document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse')), (b'link', wagtail.wagtailcore.blocks.StructBlock([(b'url', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock(required=False)), (b'label', wagtail.wagtailcore.blocks.CharBlock()), (b'style', cms.models.streamfield.LinkStyleChoiceBlock())], icon='link')), (b'embed', wagtail.wagtailembeds.blocks.EmbedBlock(icon='media')), (b'html', wagtail.wagtailcore.blocks.StructBlock([(b'html', wagtail.wagtailcore.blocks.RawHTMLBlock()), (b'alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())], icon='code', label='Raw HTML'))])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='RichTextPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'pullquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock()), (b'affiliation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'style', cms.models.streamfield.PullQuoteStyleChoiceBlock())], icon='openquote')), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.RichTextBlock()), (b'alignment', cms.models.streamfield.ImageFormatChoiceBlock())], icon='image', label='Aligned image')), (b'document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse')), (b'link', wagtail.wagtailcore.blocks.StructBlock([(b'url', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock(required=False)), (b'label', wagtail.wagtailcore.blocks.CharBlock()), (b'style', cms.models.streamfield.LinkStyleChoiceBlock())], icon='link')), (b'embed', wagtail.wagtailembeds.blocks.EmbedBlock(icon='media')), (b'html', wagtail.wagtailcore.blocks.StructBlock([(b'html', wagtail.wagtailcore.blocks.RawHTMLBlock()), (b'alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())], icon='code', label='Raw HTML'))])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
    ]
