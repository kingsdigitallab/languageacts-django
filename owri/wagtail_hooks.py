from django.conf import settings
from django.utils.html import format_html_join
from wagtail.core import hooks
from wagtail.core.whitelist import attribute_rule, check_url
# from wagtail.admin.rich_text import HalloPlugin
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler, InlineStyleElementHandler,
    ExternalLinkElementHandler, PageLinkElementHandler,
    InlineEntityElementHandler)
from draftjs_exporter.dom import DOM


@hooks.register('construct_whitelister_element_rules')
def whitelister_element_rules():
    return {
        'p': attribute_rule({'class': True}),
        'a': attribute_rule({'href': check_url, 'id': True, 'class': True,
                             'target': True}),
        'span': attribute_rule({'class': True, 'style': True}),
        'i': attribute_rule({'class': True}),
        'iframe': attribute_rule(
            {'id': True, 'class': True, 'src': True, 'style': True,
             'frameborder': True, 'allowfullscreen': True, 'width': True,
             'height': True}),
        'small': attribute_rule({'class': True})
    }


@hooks.register('register_rich_text_features')
def register_strikethrough_feature(features):
    """
    Registering the `strikethrough` feature, which uses the `STRIKETHROUGH`
    Draft.js inline style type,
    and is stored as HTML with an `<s>` tag.
    """
    feature_name = 'strikethrough'
    type_ = 'STRIKETHROUGH'
    tag = 's'
    control = {
        'type': type_,
        'label': 'S',
        'description': 'Strikethrough',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.register_converter_rule(
        'contentstate', feature_name, db_conversion)

    features.default_features.append('strikethrough')


@hooks.register('register_rich_text_features')
def register_blockquote_feature(features):
    """
    Registering the `blockquote` feature, which uses the `blockquote`
    Draft.js block type,
    and is stored as HTML with a `<blockquote>` tag.
    """
    feature_name = 'blockquote'
    type_ = 'blockquote'
    tag = 'blockquote'

    control = {
        'type': type_,
        'label': '❝',
        'description': 'Blockquote',
        'element': 'blockquote',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {tag: BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: tag}},
    })

    features.default_features.append('blockquote')


'''
# Anchor Code from:
#  https://github.com/quocduan/wagtail_draftail_anchors/tree/master
'''


def anchor_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element('a', {
        'data-anchor': True,
        # 'href': props['fragment'],
        'href': '#{}'.format(props['fragment'].lstrip('#')),
    }, props['children'])


class AnchorEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the <a> tags into ANCHOR entities, with the right data.
    """
    # In Draft.js entity terms, anchors are "mutable".
    # We can alter the anchor's text, but it's still an anchor.
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``fragment`` value from the ``href`` HTML attribute.
        """
        return {
            'fragment': attrs['href'],
        }


def anchor_identifier_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element('a', {
        # 'data-anchor': True,
        'data-id': props['fragment'].lstrip('#'),
        'id': props['fragment'].lstrip('#'),
        'href': '#{}'.format(props['fragment'].lstrip('#')),
    }, props['children'])


class AnchorIndentifierEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the <a> tags into ANCHOR IDENTIFIER
    entities, with the right data.
    """
    # In Draft.js entity terms, anchors identifier are "mutable".
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``fragment`` value from the ``href`` HTML attribute.
        """
        return {
            'fragment': attrs['href'].lstrip('#'),
            'data-id': attrs['id'],
        }


@hooks.register('register_rich_text_features')
def register_rich_text_anchor_feature(features):
    features.default_features.append('anchor')
    """
    Registering the `anchor` feature, which uses the
    `ANCHOR` Draft.js entity type,
    and is stored as HTML with a `<a data-anchor href="#my-anchor">` tag.
    """
    feature_name = 'anchor'
    type_ = 'ANCHOR'

    control = {
        'type': type_,
        'label': '#',
        'description': 'Internal Link',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more
        # complicated than for blocks and inline styles.
        'from_database_format': {
            'a[data-anchor]': AnchorEntityElementHandler(type_)},
        'to_database_format': {
            'entity_decorators': {type_: anchor_entity_decorator}},
    })


@hooks.register('insert_editor_js')
def insert_editor_js_anchor():
    js_files = [
        # We require this file here to make sure it is loaded before the other.
        'wagtailadmin/js/draftail.js',
        'js/wagtail_draftail_anchor.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
                                   ((settings.STATIC_URL, filename)
                                    for filename in js_files)
                                   )
    return js_includes



@hooks.register('register_rich_text_features')
def register_rich_text_anchor_identifier_feature(features):
    features.default_features.append('anchor-identifier')
    """
    Registering the `anchor-identifier` feature, which uses the
    `ANCHOR-IDENTIFIER` Draft.js entity type,
    and is stored as HTML with a `<a data-anchor href="#my-anchor"
    id="my-anchor">` tag.
    """
    feature_name = 'anchor-identifier'
    type_ = 'ANCHOR-IDENTIFIER'

    control = {
        'type': type_,
        'icon': 'icon icon-tag',
        'label': 'Bookmark',
        'description': 'Add Bookmark',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {
            'a[data-id]': AnchorIndentifierEntityElementHandler(type_)},
        'to_database_format': {
            'entity_decorators': {type_: anchor_identifier_entity_decorator}},
    })

# See https://github.com/wagtail/wagtail/issues/4474

@hooks.register('register_rich_text_features')
def register_extended_link_feature(features):
    features.default_features.append('extended_link')
    feature_name = 'extended_link'
    type_ = 'LINK'

    control = {
        'type': type_,
        'label': 'EX',
        'icon': 'icon icon-link',
        'description': 'External Source Link',
        'attributes': ['url', 'id', 'parentId', 'rel', 'target', 'class'],
        'whitelist': {
            'href': "^(http:|https:|undefined$)",
        }
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {
            'a[href]': ExternalLinkElementHandler('LINK'),
            'a[linktype="page"]': PageLinkElementHandler('LINK'),
        },
        'to_database_format': {
            'entity_decorators': {'LINK': extended_link_entity}
        }
    })


def extended_link_entity(props):
    id_ = props.get('id')
    link_props = {}

    if id_ is not None:
        link_props['linktype'] = 'page'
        link_props['id'] = id_
        link_props['target'] = '_blank'
        link_props['class'] = 'exsource'

    else:
        link_props['href'] = props.get('url')
        link_props['target'] = '_blank'
        link_props['class'] = 'exsource'

    return DOM.create_element('a', link_props, props['children'])


# Coloured Text

def colour_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element('span', {
        'style': 'color: {}'.format(props['fragment']),
        'data-color': props['fragment'],
    }, props['children'])


class ColourEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the <a> tags into ANCHOR entities, with the right data.
    """
    # In Draft.js entity terms, anchors are "mutable".
    # We can alter the anchor's text, but it's still an anchor.
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``fragment`` value from the ``href`` HTML attribute.
        """
        return {
            'fragment': attrs['data-color'],
        }


@hooks.register('register_rich_text_features')
def register_rich_text_colour_feature(features):
    features.default_features.append('colour')
    """
    Registering the `anchor` feature, which uses the
    `ANCHOR` Draft.js entity type,
    and is stored as HTML with a `<a data-anchor href="#my-anchor">` tag.
    """
    feature_name = 'colour'
    type_ = 'COLOUR'

    control = {
        'type': type_,
        'label': 'Color',
        'description': 'Font Colour',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more
        # complicated than for blocks and inline styles.
        'from_database_format': {
            'span[data-color]': ColourEntityElementHandler(type_)},
        'to_database_format': {
            'entity_decorators': {type_: colour_entity_decorator}},
    })


@hooks.register('insert_editor_js')
def insert_editor_js_colour():
    js_files = [
        'js/wagtail_draftail_colour.js',
    ]
    css_files = [

    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
                                   ((settings.STATIC_URL, filename)
                                    for filename in js_files)
                                   )
    js_includes = js_includes + format_html_join('\n', '<link rel="stylesheet" href="{0}{1}"/>',
                                   ((settings.STATIC_URL, filename)
                                    for filename in js_files)
                                   )
    return js_includes
