from datetime import date

from cms.models.pages import (
    BlogPost, Event, NewsPost, HomePage, BlogIndexPage,
    NewsIndexPage, EventIndexPage
)
from django import template
from django.conf import settings
from wagtail.core.models import Page

register = template.Library()


@register.filter
def get_section(current_page):
    homepage = HomePage.objects.first()
    current_section = Page.objects.ancestor_of(current_page, inclusive=True) \
        .child_of(homepage).first()
    return current_section


@register.filter
def order_by(queryset, field):
    return queryset.order_by(field)


@register.simple_tag
def are_comments_allowed():
    """Returns True if commenting on the site is allowed, False otherwise."""
    return getattr(settings, 'ALLOW_COMMENTS', False)


@register.inclusion_tag('cms/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, root, current_page):
    """Returns the pages that are part of the breadcrumb trail of the current
    page, up to the root page."""
    pages = current_page.get_ancestors(
        inclusive=True).descendant_of(root).filter(live=True)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'pages': pages}


@register.simple_tag
def get_homepage_events():
    """Returns 3 latest news posts"""
    today = date.today()
    events = Event.objects.live().filter(
        date_from__gte=today).order_by('date_from')
    if events.count() < 4:
        return events
    else:
        return events[:4]


@register.filter
def lines(val):
    if '\r\n' in val:
        return val.split('\r\n')
    else:
        return val.split('\n')


@register.filter
def related_words(page):
    return page.get_siblings(inclusive=False).live()


@register.simple_tag
def get_news_preview():
    """Returns 3 latest news posts"""
    today = date.today()
    pages = NewsPost.objects.live().filter(date__lte=today).order_by('-date')
    if pages.count() < 3:
        return pages
    else:
        return pages[:3]


@register.simple_tag
def get_blog_posts_preview():
    """Returns 3 latest blog posts"""
    today = date.today()
    pages = BlogPost.objects.live().filter(date__lte=today).order_by('-date')
    if pages.count() < 4:
        return pages
    else:
        return pages[:4]


@register.simple_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.
    Object-comparison to self will return false as objects would differ.

    :rtype: `wagtail.core.models.Page`
    """
    if hasattr(context['request'], 'site'):
        return context['request'].site.root_page
    else:
        return None


@register.simple_tag(takes_context=False)
def get_twitter_name():
    return getattr(settings, 'TWITTER_NAME')


@register.simple_tag(takes_context=False)
def get_twitter_url():
    return getattr(settings, 'TWITTER_URL')


@register.simple_tag(takes_context=False)
def get_twitter_widget_id():
    return getattr(settings, 'TWITTER_WIDGET_ID')


@register.simple_tag
def has_view_restrictions(page):
    """Returns True if the page has view restrictions set up, False
    otherwise."""
    return page.view_restrictions.count() > 0


@register.simple_tag
def show_children_in_menu(page):
    """ Force certain page types to never show children in menu"""
    if (type(page.specific) == BlogIndexPage
            or type(page.specific) == NewsIndexPage
            or type(page.specific) == EventIndexPage):
        return False
    return True


@register.inclusion_tag('cms/tags/main_menu.html', takes_context=True)
def main_menu(context, root, current_page=None):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    if not root:
        root = current_page

    menu_pages = root.get_children().live().in_menu()

    root.active = (current_page.url == root.url
                   if current_page else False)

    for page in menu_pages:
        page.active = (current_page.url.startswith(page.url)
                       if current_page else False)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'menu_pages': menu_pages}


@register.inclusion_tag('cms/tags/footer_menu.html', takes_context=True)
def footer_menu(context, root, current_page=None):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    menu_pages = root.get_children().live().in_menu()

    root.active = (current_page.url == root.url
                   if current_page else False)

    for page in menu_pages:
        page.active = (current_page.url.startswith(page.url)
                       if current_page else False)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'menu_pages': menu_pages}


@register.filter
def querify(req):
    if '?q=' in req:
        return req
    else:
        return '{}?q='.format(req)


@register.simple_tag(takes_context=True)
def get_request_parameters(context, exclude=None):
    """Returns a string with all the request parameters except the exclude
    parameter."""
    params = ''
    request = context['request']

    for key, value in request.GET.items():
        if key != exclude:
            params += '&{key}={value}'.format(key=key, value=value)

    return params


@register.simple_tag
def page_in_submenu(page: Page = None, parent: Page = None) -> bool:
    """Return true if page parent is in page's children
    (for sidebar menus) """
    if page and parent:
        for sub in parent.get_children().live().in_menu():
            if sub.pk == page.pk:
                return True
    return False
