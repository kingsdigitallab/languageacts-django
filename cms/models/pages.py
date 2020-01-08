from __future__ import unicode_literals

import logging
from datetime import date

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.shortcuts import render
from haystack.query import SearchQuerySet
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel, MultiFieldPanel, StreamFieldPanel
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from .behaviours import WithFeedImage, WithStreamField
from .streamfield import CMSStreamBlock, RecordEntryStreamBlock

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


class HomePage(Page, WithStreamField):
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


class IndexPage(Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    subpage_types = ['IndexPage', 'RichTextPage']


IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

IndexPage.promote_panels = Page.promote_panels


class StrandPage(IndexPage, WithStreamField):
    events_contextual_information = RichTextField(blank=True, null=True)

    subpage_types = ['IndexPage', 'RichTextPage', 'RecordIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def show_filtered_content(self):
        return True

    def get_context(self, request):
        context = super(StrandPage, self).get_context(request)

        context['blog_posts'] = BlogPost.get_by_strand(
            self.title)
        context['events'] = Event.get_by_strand(
            self.title)
        context['past_events'] = Event.get_past_by_strand(
            self.title)
        context['news_posts'] = NewsPost.get_by_strand(
            self.title)

        return context


StrandPage.content_panels = [
    FieldPanel('events_contextual_information'),
]


class RecordIndexPage(Page):
    search_fields = Page.search_fields + [
    ]

    subpage_types = ['RecordPage']

    def get_context(self, request):
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


class RichTextPage(Page, WithStreamField):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = []


RichTextPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

RichTextPage.promote_panels = Page.promote_panels


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


BlogIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

BlogIndexPage.promote_panels = Page.promote_panels


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('BlogPost', related_name='tagged_items')


class BlogPost(Page, WithStreamField, WithFeedImage):
    date = models.DateField()
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    strands = ParentalManyToManyField('cms.StrandPage', blank=True)
    guest = models.BooleanField(default=False, verbose_name="Guest Post")
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
        # Find closest ancestor which is a blog index
        return BlogIndexPage.objects.ancestor_of(self).last()

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


BlogPost.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('date'),
    FieldPanel('guest'),
    StreamFieldPanel('body'),
]

BlogPost.promote_panels = Page.promote_panels + [
    FieldPanel('tags'),
    ImageChooserPanel('feed_image'),

    FieldPanel('strands', widget=forms.CheckboxSelectMultiple),
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


NewsIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

NewsIndexPage.promote_panels = Page.promote_panels


class NewsPostTag(TaggedItemBase):
    content_object = ParentalKey('NewsPost', related_name='tagged_items')


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
        today = date.today()
        events = Event.objects.live().filter(
            Q(date_from__gte=today) | (
                Q(date_to__isnull=False) & Q(
                    date_to__gte=today))).order_by(
            'date_from')
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
            return self.all_posts(request)

        posts = self.posts.filter(tags__name=tag)

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
            Q(date_from__lt=today) & (
                Q(date_to__isnull=True) | Q(
                    date_to__lt=today))).order_by(
            '-date_from')
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
            return self.all_posts(request)

        posts = self.posts.filter(tags__name=tag)

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
    content_object = ParentalKey('Event', related_name='tagged_items')


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

    @classmethod
    def get_by_tag(self, tag=None):

        if tag:
            today = date.today()
            return self.objects.filter(tags__name=tag).filter(
                Q(date_from__gte=today) | (
                    Q(date_to__isnull=False) & Q(
                        date_to__gte=today))).order_by('date_from')
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
                        Q(date_to__isnull=False) & Q(
                            date_to__gte=today))).order_by('date_from')
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
                        Q(date_to__isnull=False) & Q(
                            date_to__lt=today))).order_by('date_from')
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
        context['blog'] = blog
        context['events'] = events
        context['news'] = news
        context['pages'] = pages

        # Get counts
        context['result_count'] = (
            blog.count() + events.count() +
            news.count() + pages.count())

        return render(request, self.get_template(request),
                      context)


IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    StreamFieldPanel('body'),
]

IndexPage.promote_panels = Page.promote_panels
