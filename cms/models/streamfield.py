from __future__ import unicode_literals

from django import forms
from wagtail.core.blocks import (
    CharBlock, FieldBlock, ListBlock, PageChooserBlock, RawHTMLBlock,
    RichTextBlock, StreamBlock, StructBlock, TextBlock, URLBlock
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('default', 'Default'), ('full', 'Full width'),
    ))


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()


class D3Block(StructBlock):
    html = RawHTMLBlock(required=False)
    css = RawHTMLBlock(required=False)
    js = RawHTMLBlock(required=False)
    additional_files = RawHTMLBlock(required=False,
                                    verbose_name="Additional JS\
                                    files to load.")

    class Meta:
        help_text = '''
        Enter the relevent sections.
        You don't need to add script or style tags.
        IMPORTANT: Please verify with KDL before publishing.
        Additional files should be added one file per line.
        Note: Do not include d3
        itself.'''
        template = 'cms/blocks/d3_block.html'


class HomePageBlock(StructBlock):
    url = URLBlock(required=False)
    page = PageChooserBlock(required=False)
    title = CharBlock()
    description = RichTextBlock()

    class Meta:
        template = 'cms/blocks/home_page_block.html'
        help_text = '''
        Use either URL or page, if both are filled in URL takes precedence.'''


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'),
        ('mid', 'Mid width'), ('full-width', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(required=False)
    alignment = ImageFormatChoiceBlock()
    text = RichTextBlock(required=False)

    class Meta:
        template = 'cms/blocks/image_block.html'


class ImageGrid(StructBlock):
    image = ImageChooserBlock()
    link = URLBlock(required=False)
    text = CharBlock(required=False)


class Grid(StructBlock):
    image_block = ListBlock(ImageGrid(), required=False)

    class Meta:
        template = 'cms/blocks/image_grid.html'


class LinkStyleChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('default', 'Default'), ('button', 'Button'),
    ))


class LinkBlock(StructBlock):
    url = URLBlock(required=False)
    page = PageChooserBlock(required=False)
    label = CharBlock()
    style = LinkStyleChoiceBlock()

    class Meta:
        help_text = '''
        Use either URL or page, if both are filled in URL takes precedence.'''
        template = 'cms/blocks/link_block.html'


class PullQuoteStyleChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('default', 'Default'), ('with-background', 'With background image'),
    ))


class PullQuoteBlock(StructBlock):
    quote = TextBlock('quote title')
    attribution = CharBlock()
    affiliation = CharBlock(required=False)
    style = PullQuoteStyleChoiceBlock()

    class Meta:
        template = 'cms/blocks/pull_quote_block.html'


class CMSStreamBlock(StreamBlock):
    home = HomePageBlock(icon='grip', label='Homepage Block')

    h2 = CharBlock(icon='title', classname='title')
    h3 = CharBlock(icon='title', classname='title')
    h4 = CharBlock(icon='title', classname='title')
    h5 = CharBlock(icon='title', classname='title')

    intro = RichTextBlock(icon='pilcrow')
    paragraph = RichTextBlock(icon='pilcrow')
    pullquote = PullQuoteBlock(icon='openquote')

    image = ImageBlock(label='Aligned image + text', icon='image')
    grid = Grid(icon='grip', label='Image grid')
    document = DocumentChooserBlock(icon='doc-full-inverse')
    link = LinkBlock(icon='link')
    embed = EmbedBlock(icon='media')

    html = AlignedHTMLBlock(icon='code', label='Raw HTML')

    d3 = D3Block(icon='media', label='D3 Visualisation')

    table = TableBlock()
