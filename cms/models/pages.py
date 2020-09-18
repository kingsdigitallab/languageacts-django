from __future__ import unicode_literals

import logging
from datetime import date

# from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q, QuerySet
from django.shortcuts import render
from django.utils.text import slugify
from haystack.query import SearchQuerySet
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel, MultiFieldPanel, StreamFieldPanel
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from .behaviours import WithFeedImage, WithStreamField
from .streamfield import RecordEntryStreamBlock, CMSStreamBlock

logger = logging.getLogger(__name__)


def _paginate(request, items):
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(items, settings.ITEMS_PER_PAGE)

    try:
        items = paginator.page(page)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        items = paginator.page(1)

    return items


class StrandChildMixin(object):
    """Quick mixin to get a parent strand from Treebeard(wagtail)
    parent tree.  Looks at all ancestors"""

    @property
    def parent_strands(self):
        return StrandPage.objects.ancestor_of(self).specific()

    def add_parent_strand_content_to_context(self, context):
        if self.parent_strands.count() > 0:
            # Right now this assumes 1 strand parent
            # will need to be refactored IF strands manymany actually used
            for strand in self.parent_strands:
                context['strand'] = strand
                context = StrandPage.get_strand_related_content(
                    context, strand.title)
        return context


class IndexPage(StrandChildMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    subpage_types = ['IndexPage', 'RichTextPage']

    def get_context(self, request, *args, **kwargs):
        context = super(IndexPage, self).get_context(request)
        context = self.add_parent_strand_content_to_context(context)
        return context


IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

IndexPage.promote_panels = Page.promote_panels


class StrandPage(IndexPage, WithStreamField):
    blogs_contextual_information = RichTextField(blank=True, null=True)
    events_contextual_information = RichTextField(blank=True, null=True)
    news_contextual_information = RichTextField(blank=True, null=True)

    subpage_types = ['IndexPage', 'RichTextPage', 'RecordIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def show_filtered_content(self):
        return True

    @classmethod
    def get_strand_related_content(cls, context: dict, title: str) -> dict:
        """ Add posts, events, news for strand to context"""
        if context and title:
            context['blog_posts'] = BlogPost.get_by_strand(
                title)
            context['events'] = Event.get_by_strand(
                title)
            context['past_events'] = Event.get_past_by_strand(
                title)
            context['news_posts'] = NewsPost.get_by_strand(
                title)
        return context

    def get_context(self, request, *args, **kwargs):
        context = super(StrandPage, self).get_context(request)
        context['strand'] = self
        context = StrandPage.get_strand_related_content(context, self.title)
        return context


StrandPage.content_panels = [
    FieldPanel('blogs_contextual_information'),
    FieldPanel('events_contextual_information'),
    FieldPanel('news_contextual_information'),
]


class RecordIndexPage(Page):
    search_fields = Page.search_fields + [
    ]

    subpage_types = ['RecordPage']

    def get_context(self, request, *args, **kwargs):
        context = super(RecordIndexPage, self).get_context(request)

        # Get selected facets
        selected_facets = set(request.GET.getlist('selected_facets'))

        # Init a search query set
        sqs = SearchQuerySet().models(RecordPage)

        # Apply currently selected facets
        for facet in selected_facets:
            sqs = sqs.narrow(facet)

        # Get facet counts
        sqs = sqs.facet('language').facet('word_type').facet('first_letter')

        # Generate presentable facet data
        selected_facets_ui = []

        for facet in selected_facets:
            f = {
                'value': facet.split(':')[1],
                'remove_url': request.get_full_path().replace(
                    '&selected_facets={}'.format(facet), '')
            }
            selected_facets_ui.append(f)

        context['selected_facets'] = selected_facets_ui
        context['sqs'] = sqs

        return context


RecordIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
]

RecordIndexPage.promote_panels = Page.promote_panels


class RecordPage(Page):
    latin_lemma = RichTextField(blank=True, null=True)

    latin_pos = ParentalManyToManyField('cms.POSLabel', blank=True)

    latin_meaning = RichTextField(blank=True, null=True)

    cultural_transmission = StreamField(
        CMSStreamBlock(required=False, blank=True))

    search_fields = Page.search_fields + [
    ]

    subpage_types = ['RecordEntry']

    def get_languages(self):
        return RecordEntry.objects.live().descendant_of(self).order_by(
            'language__order_by')


RecordPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('latin_lemma'),
    FieldPanel('latin_pos', widget=forms.CheckboxSelectMultiple),
    FieldPanel('latin_meaning'),
    StreamFieldPanel('cultural_transmission')
]

RecordPage.promote_panels = Page.promote_panels


class RecordEntry(Page):
    language = models.ForeignKey(
        'cms.LemmaLanguage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    lemma = models.CharField(
        max_length=2048, blank=True, null=True)

    variants = StreamField(RecordEntryStreamBlock, blank=True)

    pos = ParentalManyToManyField('cms.POSLabel', blank=True)

    morph_related_words = StreamField(RecordEntryStreamBlock, blank=True)
    ranking_freq = StreamField(RecordEntryStreamBlock, blank=True)
    first_attest = StreamField(RecordEntryStreamBlock, blank=True)
    hist_freq = StreamField(RecordEntryStreamBlock, blank=True,
                            verbose_name='Historical frequency')
    hist_freq_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='[OR] Pre-rendered Graph Image',
        help_text='Pre-rendered graph will take priority over manual data\
            inputted above.'
    )
    semantic_history = StreamField(RecordEntryStreamBlock, blank=True)
    collocational_history = StreamField(RecordEntryStreamBlock, blank=True)
    diatopic_variation = StreamField(RecordEntryStreamBlock, blank=True)
    diaphasic_variation = StreamField(RecordEntryStreamBlock, blank=True)

    search_fields = Page.search_fields + [
    ]

    subpage_types = []

    @property
    def url(self):
        return self.get_parent().url


RecordEntry.content_panels = [
    FieldPanel('title', classname='full title'),
    SnippetChooserPanel('language'),
    FieldPanel('lemma'),
    StreamFieldPanel('variants'),
    FieldPanel('pos', widget=forms.CheckboxSelectMultiple),
    StreamFieldPanel('morph_related_words'),
    StreamFieldPanel('ranking_freq'),
    StreamFieldPanel('first_attest'),
    MultiFieldPanel(
        [
            StreamFieldPanel('hist_freq'),
            ImageChooserPanel('hist_freq_image')
        ],
        heading='Historical Frequency (per million words)',
        classname="collapsible collapsed"
    ),
    StreamFieldPanel('semantic_history'),
    StreamFieldPanel('collocational_history'),
    StreamFieldPanel('diatopic_variation'),
    StreamFieldPanel('diaphasic_variation'),
]


class RichTextPage(StrandChildMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super(RichTextPage, self).get_context(request)
        context = self.add_parent_strand_content_to_context(context)
        return context


RichTextPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

RichTextPage.promote_panels = Page.promote_panels


@register_snippet
class BlogAuthor(models.Model):
    author_name = models.CharField(max_length=512, default='')
    first_name = models.CharField(max_length=512, default='')
    last_name = models.CharField(max_length=512, default='')
    author_slug = models.CharField(max_length=512, default='')

    def save(self, *args, **kwargs):
        # update author slug
        self.author_slug = slugify(self.author_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.author_name


class BlogIndexPage(RoutablePageMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = ['BlogPost']

    @property
    def posts(self):
        today = date.today()
        posts = BlogPost.objects.live().descendant_of(
            self).filter(date__lte=today)

        posts = posts.order_by('-date')

        return posts

    @route(r'^$')
    def all_posts(self, request):
        posts = self.posts

        return render(request, self.get_template(request),
                      {'self': self, 'posts': _paginate(request, posts)})

    @route(r'^tag/(?P<tag>[\w\- ]+)/$')
    def tag(self, request, tag=None):
        if not tag:
            # Invalid tag filter
            logger.error('Invalid tag filter')
            return self.all_posts(request)

        posts = self.posts.filter(tags__name=tag)

        return render(
            request, self.get_template(request), {
                'self': self, 'posts': _paginate(request, posts),
                'filter_type': 'tag', 'filter': tag
            }
        )

    def get_author(self, author_slug: str) -> QuerySet:
        if author_slug:
            return self.posts.filter(
                author__author_slug=author_slug
            )
        return BlogAuthor.objects.none()

    @route(r'^author/(?P<author>[\w\- ]*)/$')
    def author(self, request, author=None):
        posts = self.get_author(author)
        return render(
            request, self.get_template(request), {
                'self': self, 'posts': _paginate(request, posts),
                'filter_type': 'author', 'filter': author
            }
        )


BlogIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

BlogIndexPage.promote_panels = Page.promote_panels


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPost',
        on_delete=models.CASCADE, related_name='tagged_items')

    @property
    def name(self):
        """This has been added because of an error in
        _edit_string_for_tags(tags) in taggit getting the parent object
        not the tag, and failing with an Attribute Error. May need to be
        revisited"""
        if self.tag:
            return self.tag.name
        return ''


class BlogPost(Page, WithStreamField, WithFeedImage):
    date = models.DateField()
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    guest = models.BooleanField(default=False,
                                verbose_name="Guest Post",
                                help_text='Create new guest author in snippets'
                                )
    author = models.ForeignKey('BlogAuthor',
                               verbose_name="Author",
                               blank=True, null=True,
                               on_delete=models.SET_NULL,
                               help_text=("select guest author or leave blank"
                                          " for default user")
                               )
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('date'),
        index.SearchField('author'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
            index.SearchField('slug'),
        ]),
    ]

    subpage_types = []

    def get_index_page(self):
        # Find closest ancestor which is a blog index
        return BlogIndexPage.objects.ancestor_of(self).last()

    def save(self, *args, **kwargs):
        if not self.author:
            # set the author to either the current user
            # or if guest is checked, the generic guest author
            if self.guest:
                try:
                    self.author = BlogAuthor.objects.get(author_name='guest')
                except ObjectDoesNotExist:
                    logger.error("Generic Guest Author does not exist!")
                    return
            else:
                try:
                    self.author = BlogAuthor.objects.get(
                        author_name=self.owner.username
                    )
                except ObjectDoesNotExist:
                    # Author for this user does not exist, create one
                    author, created = BlogAuthor.objects.get_or_create(
                        author_name=self.owner.username,
                        first_name=self.owner.first_name,
                        last_name=self.owner.last_name,
                    )
                    self.author = author

        super().save(*args, **kwargs)

    @classmethod
    def get_by_tag(cls, tag=None):
        today = date.today()
        if tag:
            return cls.objects.live().filter(
                tags__name=tag).filter(date__lte=today).order_by('-date')
        else:
            return cls.objects.none()

    @classmethod
    def get_by_author(cls, author=None):
        if author:
            return cls.objects.live().filter(author__author_name=author)
        return cls.objects.none()

    @classmethod
    def get_by_strand(cls, strand_name=None):
        today = date.today()
        if strand_name:
            try:
                strand = StrandPage.objects.get(title=strand_name)
                return cls.objects.live().filter(
                    strands=strand).filter(date__lte=today).order_by('-date')
            except ObjectDoesNotExist:
                return cls.objects.none()
        else:
            return cls.objects.none()


BlogPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    MultiFieldPanel([
        FieldPanel('guest'),
        FieldPanel('author'),
    ]),
    StreamFieldPanel('body'),
]

BlogPost.promote_panels = Page.promote_panels + [
    FieldPanel('tags'),
    ImageChooserPanel('feed_image'),
    FieldPanel('strands', widget=forms.CheckboxSelectMultiple),
]

BlogPost.settings_panels = Page.settings_panels + [
    FieldPanel('owner'),
]


# News pages
class NewsIndexPage(RoutablePageMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = ['NewsPost']

    @property
    def posts(self):
        today = date.today()
        posts = NewsPost.objects.live().descendant_of(
            self).filter(date__lte=today)

        posts = posts.order_by('-date')

        return posts

    @route(r'^$')
    def all_posts(self, request):
        posts = self.posts

        return render(request, self.get_template(request),
                      {'self': self, 'posts': _paginate(request, posts)})

    @route(r'^tag/(?P<tag>[\w\-\_ ]+)/$')
    def tag(self, request, tag=None):
        if not tag:
            # Invalid tag filter
            logger.error('Invalid tag filter')
            return self.all_posts(request)

        posts = self.posts.filter(tags__name=tag)

        return render(
            request, self.get_template(request), {
                'self': self, 'posts': _paginate(request, posts),
                'filter_type': 'tag', 'filter': tag
            }
        )


NewsIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

NewsIndexPage.promote_panels = Page.promote_panels


class NewsPostTag(TaggedItemBase):
    content_object = ParentalKey(
        'NewsPost', on_delete=models.CASCADE, related_name='tagged_items'
    )

    @property
    def name(self):
        if self.tag:
            return self.tag.name
        return ''


class NewsPost(Page, WithStreamField, WithFeedImage):
    date = models.DateField()
    tags = ClusterTaggableManager(through=NewsPostTag, blank=True)
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('date'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
            index.SearchField('slug'),
        ]),
    ]

    subpage_types = []

    def get_index_page(self):
        # Find closest ancestor which is a news index
        return NewsIndexPage.objects.ancestor_of(self).last()

    @classmethod
    def get_by_tag(self, tag=None):
        today = date.today()
        if tag:
            return self.objects.live().filter(
                tags__name=tag).filter(date__lte=today).order_by('-date')
        else:
            return self.objects.none()

    @classmethod
    def get_by_strand(self, strand_name=None):
        today = date.today()
        if strand_name:
            try:
                strand = StrandPage.objects.get(title=strand_name)
                return self.objects.live().filter(
                    strands=strand).filter(date__lte=today).order_by('-date')
            except ObjectDoesNotExist:
                return self.objects.none()
        else:
            return self.objects.none()


NewsPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    StreamFieldPanel('body'),
]

NewsPost.promote_panels = Page.promote_panels + [
    FieldPanel('tags'),
    ImageChooserPanel('feed_image'),
    FieldPanel('strands', widget=forms.CheckboxSelectMultiple),
]


class EventIndexPage(RoutablePageMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = ['Event', 'PastEventIndexPage']

    @property
    def events(self):
        # Events that have not ended.
        events = Event.objects.live().filter().order_by('-date_from')
        return events

    @route(r'^$')
    def all_events(self, request):
        events = self.events

        return render(request, self.get_template(request),
                      {'self': self, 'paginated_events': _paginate(
                          request, events)})

    @route(r'^tag/(?P<tag>[\w\- ]+)/$')
    def tag(self, request, tag=None):
        if not tag:
            # Invalid tag filter
            logger.error('Invalid tag filter')
            return self.all_events(request)

        posts = self.events.filter(tags__name=tag)

        return render(
            request, self.get_template(request), {
                'self': self, 'events': _paginate(request, posts),
                'filter_type': 'tag', 'filter': tag
            }
        )


EventIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

EventIndexPage.promote_panels = Page.promote_panels


class PastEventIndexPage(RoutablePageMixin, Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = []

    @property
    def events(self):
        # Events that have not ended.
        today = date.today()
        events = Event.objects.live().filter(
            Q(date_from__lt=today) & (Q(date_to__isnull=True) | Q(
                date_to__lt=today))
        ).order_by('-date_from')
        return events

    @route(r'^$')
    def all_events(self, request):
        events = self.events
        return render(request, self.get_template(request),
                      {'self': self, 'events': _paginate(request, events)})

    @route(r'^tag/(?P<tag>[\w\- ]+)/$')
    def tag(self, request, tag=None):
        if not tag:
            # Invalid tag filter
            logger.error('Invalid tag filter')
            return self.all_events(request)

        posts = self.events.filter(tags__name=tag)

        return render(
            request, self.get_template(request), {
                'self': self, 'events': _paginate(request, posts),
                'filter_type': 'tag', 'filter': tag
            }
        )


PastEventIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

PastEventIndexPage.promote_panels = Page.promote_panels


class EventTag(TaggedItemBase):
    content_object = ParentalKey(
        'Event', on_delete=models.CASCADE, related_name='tagged_items')

    @property
    def name(self):
        if self.tag:
            return self.tag.name
        return ''


class Event(Page, WithStreamField, WithFeedImage):
    date_from = models.DateField(verbose_name="Start Date")
    date_to = models.DateField(verbose_name="End Date (Leave blank if\
                               not required)", blank=True, null=True)
    time = models.TimeField(verbose_name="Time of Event")
    time_end = models.TimeField(verbose_name="End Time (leave blank if\
                                not required)", blank=True, null=True)

    location = models.TextField(verbose_name="Location")

    tags = ClusterTaggableManager(through=EventTag, blank=True)
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('date_from'),
        index.SearchField('date_to'),
        index.RelatedFields('tags', [
            index.SearchField('name'),
            index.SearchField('slug'),
        ]),
    ]

    subpage_types = []

    def get_index_page(self):
        # Find closest ancestor which is a blog index
        return EventIndexPage.objects.ancestor_of(self).last()

    @property
    def is_past(self):
        return date.today() > self.date_from and (
            self.date_to is None or date.today() > self.date_to
        )

    @classmethod
    def get_by_tag(self, tag=None):
        if tag:
            today = date.today()
            return self.objects.filter(tags__name=tag).filter(
                Q(date_from__gte=today)
                | (Q(date_to__isnull=False) & Q(date_to__gte=today))
            ).order_by('date_from')
        else:
            return self.objects.none()

    @classmethod
    def get_by_strand(self, strand_name=None):
        if strand_name:
            try:
                today = date.today()
                strand = StrandPage.objects.get(title=strand_name)
                return self.objects.filter(strands=strand).filter(
                    Q(date_from__gte=today) | (
                        Q(date_to__isnull=False) & Q(date_to__gte=today))
                ).order_by('date_from')
            except ObjectDoesNotExist:
                return self.objects.none()
        else:
            return self.objects.none()

    @classmethod
    def get_past_by_strand(self, strand_name=None):
        if strand_name:
            try:
                today = date.today()
                strand = StrandPage.objects.get(title=strand_name)
                return self.objects.filter(strands=strand).filter(
                    Q(date_from__lt=today) | (
                        Q(date_to__isnull=False) & Q(date_to__lt=today))
                ).order_by('date_from')
            except ObjectDoesNotExist:
                return self.objects.none()
        else:
            return self.objects.none()


Event.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date_from'),
    FieldPanel('date_to'),
    FieldPanel('time'),
    FieldPanel('time_end'),
    FieldPanel('location'),
    StreamFieldPanel('body'),
]

Event.promote_panels = Page.promote_panels + [
    FieldPanel('tags'),
    ImageChooserPanel('feed_image'),
    FieldPanel('strands', widget=forms.CheckboxSelectMultiple),
]


class TagResults(RoutablePageMixin, Page):

    @route(r'^$')
    def results(self, request):
        context = {
            'blog': None,
            'events': None,
            'news': None,
            'pages': None,
            'result_count': 0,
            'self': self
        }

        # Sanity checking
        if 'tag' in request.GET:
            tag = request.GET['tag']
        else:
            context['result_count'] = 0
            return render(request, self.get_template(request),
                          context)

        # Check if we have a strand, and if so, get that strand
        # page's children
        try:
            strand = StrandPage.objects.get(title=tag)
            pages = strand.get_children()
        except ObjectDoesNotExist:
            pages = StrandPage.objects.none()

        # Get tagged content
        blog_tag = BlogPost.get_by_tag(tag)
        blog_strand = BlogPost.get_by_strand(tag)
        events_tag = Event.get_by_tag(tag)
        events_strand = Event.get_by_strand(tag)
        news_tag = NewsPost.get_by_tag(tag)
        news_strand = NewsPost.get_by_strand(tag)

        # Merge tagged content
        blog = blog_tag | blog_strand
        events = events_tag | events_strand
        news = news_tag | news_strand

        # Assign them
        context['blog'] = blog.distinct()
        context['events'] = events.distinct()
        context['news'] = news.distinct()
        context['pages'] = pages.distinct()

        # Get counts
        context['result_count'] = (
            blog.count() + events.count() + news.count() + pages.count()
        )

        return render(request, self.get_template(request),
                      context)


IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

IndexPage.promote_panels = Page.promote_panels

""" Carousel Blocks """


class BaseSlideBlock(blocks.StructBlock):
    """Core methods for all carousel slides"""

    class Meta:
        abstract = True
        template = 'cms/blocks/slide_block.html'

    @staticmethod
    def get_slide_data_from_page(context, post):
        """Extract slide data from page with feedimage"""
        context['page'] = post
        context['title'] = post.title
        context['description'] = post.search_description
        context['url'] = post.url
        if post.feed_image:
            context['image'] = post.feed_image
        return context

    @staticmethod
    def get_default_values(value: dict, context: dict) -> dict:
        """Get the default slide fields from value dict
        return context"""
        if 'title' in value and value['title'] is not None:
            context['title'] = value['title']
        if 'description' in value and value['description'] is not None:
            context['description'] = value['description']
        if 'heading' in value and value['heading'] is not None:
            context['heading'] = value['heading']
        return context


class SlideBlock(BaseSlideBlock):
    """A basic slide to be used in a carousel block"""
    title = blocks.CharBlock(required=True)
    heading = blocks.CharBlock(
        required=False,
        default='',
        label='Section heading'
    )
    description = blocks.RichTextBlock(required=False)
    url = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False, help_text='Overrides url')
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, label='Image caption')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = BaseSlideBlock.get_default_values(value, context)
        if 'page' in value and value['page'] is not None:
            context['url'] = value['page'].url
        else:
            context['url'] = value['url']
        context['image'] = value['image']
        context['caption'] = value['caption']
        return context

    class Meta:
        template = 'cms/blocks/slide_block.html'


class BlogSlideBlock(BaseSlideBlock):
    """Link to blog pages
    use_latest overrides selection to show most recent post"""
    page = blocks.PageChooserBlock(required=False, page_type=BlogPost)
    caption = blocks.CharBlock(required=False)
    heading = blocks.CharBlock(required=False, default='Blog')
    css_class = 'blog-section'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = BaseSlideBlock.get_default_values(value, context)
        context = BaseSlideBlock.get_slide_data_from_page(
            context,
            value['page']
        )
        context['caption'] = value['caption']
        context['css_class'] = 'blog-section'
        return context


class NewsSlideBlock(BaseSlideBlock):
    """Link to news pages
    use_latest overrides selection to show most recent post"""
    page = blocks.PageChooserBlock(required=False, page_type=NewsPost)
    caption = blocks.CharBlock(required=False)
    heading = blocks.CharBlock(required=False, default='News')
    css_class = 'news-section'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = BaseSlideBlock.get_default_values(value, context)
        context = BaseSlideBlock.get_slide_data_from_page(
            context,
            value['page']
        )
        if 'heading' in value and value['heading'] is not None:
            context['heading'] = value['heading']
        context['caption'] = value['caption']
        context['css_class'] = 'news-section'
        return context

    class Meta:
        template = 'cms/blocks/slide_block.html'


class EventSlideBlock(BaseSlideBlock):
    """Slide based on event
    if use_upcoming template will show most_recent upcoming event """
    page = blocks.PageChooserBlock(required=True, page_type=Event)
    caption = blocks.CharBlock(required=False)
    heading = blocks.CharBlock(required=False, default='Event')
    css_class = 'events-section'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = BaseSlideBlock.get_default_values(value, context)
        context = BaseSlideBlock.get_slide_data_from_page(context,
                                                          value['page'])

        context['caption'] = value['caption']
        context['css_class'] = 'events-section'
        return context


class UpcomingEventSlideBlock(blocks.StaticBlock):
    css_class = 'events-section'

    class Meta:
        icon = 'date'
        label = 'Upcoming event'
        admin_text = 'Show next upcoming event'
        template = 'cms/blocks/slide_block.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        event = None
        if Event.objects.live().filter(
                date_from__gte=date.today()
        ).order_by('date_from').count() > 0:
            event = Event.objects.live().filter(
                date_from__gte=date.today()
            ).order_by('date_from')[0]
        elif Event.objects.live().order_by('-date_from').count() > 0:
            # No upcoming events, use most recent instead
            event = Event.objects.live().order_by('-date_from')[0]
        if event:
            context = BaseSlideBlock.get_slide_data_from_page(context, event)
        context['heading'] = 'Upcoming Event'
        context['css_class'] = 'events-section'
        # context['caption'] = post.feed_image.caption
        return context


class LatestBlogSlideBlock(blocks.StaticBlock):
    css_class = 'blog-section'

    class Meta:
        icon = 'edit'
        label = 'Latest blog post'
        admin_text = 'Latest blog post'
        template = 'cms/blocks/slide_block.html'

    def get_post(self):
        posts = BlogPost.objects.filter(live=True).order_by('-date')
        if posts and posts.count() > 0:
            return posts[0]
        return None

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = BaseSlideBlock.get_slide_data_from_page(
            context,
            self.get_post()
        )
        context['heading'] = 'Latest Post'
        context['css_class'] = 'blog-section'
        # context['caption'] = post.feed_image.caption
        return context


class LatestNewsSlideBlock(LatestBlogSlideBlock):
    css_class = 'news-section'

    class Meta:
        icon = 'doc-empty-inverse'
        label = 'Latest news'
        admin_text = 'Latest news'
        template = 'cms/blocks/slide_block.html'

    def get_post(self):
        posts = NewsPost.objects.filter(live=True).order_by('-date')
        if posts and posts.count() > 0:
            return posts[0]
        return None

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['heading'] = 'Latest News'
        context['css_class'] = 'news-section'
        return context


class CarouselBlock(blocks.StreamBlock):
    slides = SlideBlock(label='Slide', icon='image')
    blog_slide = BlogSlideBlock(label='Blog slide', icon='edit')
    latest_news = LatestNewsSlideBlock()
    latest_post = LatestBlogSlideBlock()
    next_event = UpcomingEventSlideBlock()
    event_slide = EventSlideBlock(label='Event slide', icon='date')
    news_slide = NewsSlideBlock(label='News slide', icon='edit')

    class Meta:
        template = 'cms/blocks/carousel_block.html'
        icon = 'image'


class CarouselCMSStreamBlock(CMSStreamBlock):
    carousel = CarouselBlock()


class HomePage(Page):
    body = StreamField(CarouselCMSStreamBlock())
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = [
        'BlogIndexPage', 'EventIndexPage', 'IndexPage',
        'NewsIndexPage', 'PastEventIndexPage', 'RichTextPage',
        'StrandPage', 'TagResults'
    ]


HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

HomePage.promote_panels = Page.promote_panels
