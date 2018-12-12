# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-12-12 11:26
from __future__ import unicode_literals

import cms.models.streamfield
from django.db import migrations, models
import django.db.models.deletion
import wagtail.contrib.table_block.blocks
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks
import wagtail.wagtailembeds.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        ('cms', '0023_recordpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'home', wagtail.wagtailcore.blocks.StructBlock([(b'url', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock(required=False)), (b'title', wagtail.wagtailcore.blocks.CharBlock()), (b'description', wagtail.wagtailcore.blocks.RichTextBlock())], icon='grip', label='Homepage Block')), (b'h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), (b'intro', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), (b'pullquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock()), (b'affiliation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'style', cms.models.streamfield.PullQuoteStyleChoiceBlock())], icon='openquote')), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.RichTextBlock(required=False)), (b'alignment', cms.models.streamfield.ImageFormatChoiceBlock()), (b'text', wagtail.wagtailcore.blocks.RichTextBlock(required=False))], icon='image', label='Aligned image + text')), (b'grid', wagtail.wagtailcore.blocks.StructBlock([(b'image_block', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'link', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'text', wagtail.wagtailcore.blocks.CharBlock(required=False))]), required=False))], icon='grip', label='Image grid')), (b'document', wagtail.wagtaildocs.blocks.DocumentChooserBlock(icon='doc-full-inverse')), (b'link', wagtail.wagtailcore.blocks.StructBlock([(b'url', wagtail.wagtailcore.blocks.URLBlock(required=False)), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock(required=False)), (b'label', wagtail.wagtailcore.blocks.CharBlock()), (b'style', cms.models.streamfield.LinkStyleChoiceBlock())], icon='link')), (b'embed', wagtail.wagtailembeds.blocks.EmbedBlock(icon='media')), (b'html', wagtail.wagtailcore.blocks.StructBlock([(b'html', wagtail.wagtailcore.blocks.RawHTMLBlock()), (b'alignment', cms.models.streamfield.HTMLAlignmentChoiceBlock())], icon='code', label='Raw HTML')), (b'd3', wagtail.wagtailcore.blocks.StructBlock([(b'html', wagtail.wagtailcore.blocks.RawHTMLBlock(required=False)), (b'css', wagtail.wagtailcore.blocks.RawHTMLBlock(required=False)), (b'js', wagtail.wagtailcore.blocks.RawHTMLBlock(required=False)), (b'additional_files', wagtail.wagtailcore.blocks.RawHTMLBlock(required=False, verbose_name='Additional JS                                    files to load.'))], icon='media', label='D3 Visualisation')), (b'table', wagtail.contrib.table_block.blocks.TableBlock())])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
    ]