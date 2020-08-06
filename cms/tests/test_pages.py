# BlogPost,
from datetime import date
from typing import Union, Optional
from unittest.mock import MagicMock, create_autospec, patch

import factory
from cms.models.pages import (
    BlogIndexPage, EventIndexPage, HomePage, IndexPage, NewsIndexPage,
    PastEventIndexPage, RichTextPage, StrandPage, _paginate, TagResults,
    BlogAuthor, BlogPost, NewsPost, Event
)
from cms.tests.factories import (
    BlogIndexPageFactory, BlogPostFactory, BlogAuthorFactory,
    NewsIndexPageFactory, NewsPostFactory, StrandPageFactory,
    EventIndexPageFactory, PastEventIndexPageFactory,
    EventFactory, UserFactory
)
from cms.views.search import SearchView
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse
from wagtail.core.models import Page
from wagtail.search.backends.elasticsearch2 import Elasticsearch2SearchResults
from wagtail.tests.utils import WagtailPageTests

""" Helper functions to make trees of wagtail objects for tests  """


def create_site_root() -> Page:
    home_page, created = Page.objects.get_or_create(id=2)
    return home_page


def create_blog_index(parent: Optional[Page],
                      title: str = 'Default Blog Index') -> [Page,
                                                             BlogIndexPage]:
    if parent is None:
        parent = create_site_root()
    index = BlogIndexPageFactory.build(
        title=title
    )
    parent.add_child(
        instance=index
    )
    return parent, index


def create_blog_post(
        parent: Optional[BlogIndexPage], author: BlogAuthor, **kwargs
) -> [Union[BlogIndexPage, None], BlogPost]:
    if parent is None:
        parent = create_blog_index('Default Blog Index')
    blog_1 = BlogPostFactory.build(**kwargs)
    blog_1.author = author
    parent.add_child(
        instance=blog_1
    )
    return parent, blog_1


class TestPages(TestCase):

    def test__paginate(self):
        items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

        factory = RequestFactory()

        request = factory.get('/test?page=1')
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                         _paginate(request, items).object_list)
        request = factory.get('/test?page=2')
        self.assertEqual([10, 11, 12, 13, 14, 15, 16, 17],
                         _paginate(request, items).object_list)
        request = factory.get('/test?page=10')
        self.assertEqual([10, 11, 12, 13, 14, 15, 16, 17],
                         _paginate(request, items).object_list)
        request = factory.get('/test?page=a')
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                         _paginate(request, items).object_list)


class TestStrandPage(TestCase):

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.blog_index_page = BlogIndexPageFactory.build(
            title='Blog Index Test'
        )
        self.home_page.add_child(
            instance=self.blog_index_page
        )

    def test_show_filtered_content(self):
        strand_1 = StrandPageFactory.build()
        self.assertTrue(strand_1.show_filtered_content())

    def test_get_context(self):
        strand_1 = StrandPageFactory.build()
        self.home_page.add_child(
            instance=strand_1
        )
        self.blog_1 = BlogPostFactory.build(
            author=BlogAuthorFactory()
        )
        self.blog_index_page.add_child(
            instance=self.blog_1
        )
        self.blog_1.strands.add(strand_1)
        self.blog_1.save()
        factory = RequestFactory()
        request = factory.get('/test_strand')
        context = strand_1.get_context(request)
        blog_posts = context['blog_posts']
        self.assertEqual(blog_posts.count(), 1)
        self.assertEqual(blog_posts[0], self.blog_1)


class TestHomePage(WagtailPageTests):
    fixtures = ['tests.json']

    def test_subpage_types(self):
        self.assertAllowedSubpageTypes(
            HomePage, {
                BlogIndexPage,
                EventIndexPage,
                IndexPage,
                NewsIndexPage,
                PastEventIndexPage,
                RichTextPage,
                StrandPage,
                TagResults
            })


class TestIndexPage(WagtailPageTests):
    fixtures = ['tests.json']

    def test_subpage_types(self):
        self.assertAllowedSubpageTypes(IndexPage, {IndexPage, RichTextPage})

    # def test_render(self) -> None:
    #     import pdb
    #     pdb.set_trace()
    #     ip = IndexPage.objects.all()[0]
    #     response = self.client.get(
    #         ip.url
    #     )
    #     self.assertEqual(response.status_code, 200)


class TestRichTextPage(WagtailPageTests):
    fixtures = ['tests.json']

    def test_subpage_types(self):
        self.assertAllowedSubpageTypes(RichTextPage, {})


class TestBlogPost(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = BlogAuthorFactory()
        cls.author_2 = BlogAuthorFactory()
        cls.home_page, cls.blog_index_page = create_blog_index(None)
        cls.blog_index_page, cls.blog_1 = create_blog_post(
            cls.blog_index_page, cls.author_1)

    def test_get_index_page(self) -> None:
        self.assertEqual(
            self.blog_1.get_index_page(),
            BlogIndexPage.objects.ancestor_of(self.blog_1).last()
        )

    def test_save(self) -> None:
        self.blog_1.author = None
        owner = UserFactory()
        self.blog_1.owner = owner
        # No author, not a guest, set owner
        self.blog_1.save()
        self.assertEqual(self.blog_1.author.author_name, owner.username)
        # No author, guest
        self.blog_1.author = None
        self.blog_1.guest = True
        self.blog_1.save()
        self.assertEqual(self.blog_1.author.author_name, 'guest')
        # New author, save as normal
        author_3 = BlogAuthorFactory()
        self.blog_1.author = author_3
        self.blog_1.save()
        self.assertEqual(
            self.blog_1.author.author_name, author_3.author_name)

    def test_get_by_tag(self) -> None:
        self.blog_1.tags.add('test-tag')
        self.blog_1.save()
        posts = BlogPost.get_by_tag('test-tag')
        self.assertEqual(posts.count(), 1)
        posts = BlogPost.get_by_tag('bad-tag')
        self.assertQuerysetEqual(posts, BlogPost.objects.none())

    def test_get_by_author(self) -> None:
        self.assertQuerysetEqual(
            BlogPost.get_by_author(None), BlogPost.objects.none())
        self.assertEqual(
            BlogPost.get_by_author(self.author_1).count(), 1)
        self.assertQuerysetEqual(
            BlogPost.get_by_author(BlogAuthorFactory()),
            BlogPost.objects.none()
        )

    def test_get_by_strand(self) -> None:
        strand_1 = StrandPageFactory.build()
        strand_2 = StrandPageFactory.build()
        self.home_page.add_child(
            instance=strand_1
        )
        self.home_page.add_child(
            instance=strand_2
        )
        self.blog_1.strands.add(strand_1)
        self.blog_1.save()
        self.assertQuerysetEqual(
            BlogPost.get_by_strand(None), BlogPost.objects.none())
        self.assertQuerysetEqual(
            BlogPost.get_by_strand('bad strand name'), BlogPost.objects.none()
        )
        self.assertEqual(
            BlogPost.get_by_strand(strand_1).count(),
            1
        )
        self.assertEqual(BlogPost.get_by_strand(strand_1)[0], self.blog_1)
        self.assertQuerysetEqual(
            BlogPost.get_by_strand(strand_2), BlogPost.objects.none())


class TestNewsPost(TestCase):

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.news_index = NewsIndexPageFactory.build(
            title='News Index Test'
        )
        self.home_page.add_child(
            instance=self.news_index
        )
        self.news_1 = NewsPostFactory.build()
        self.news_index.add_child(
            instance=self.news_1
        )

    def test_get_index_page(self) -> None:
        self.assertEqual(
            self.news_1.get_index_page(),
            NewsIndexPage.objects.ancestor_of(self.news_1).last()
        )

    def test_get_by_tag(self) -> None:
        self.news_1.tags.add('test-tag')
        self.news_1.save()
        posts = NewsPost.get_by_tag('test-tag')
        self.assertEqual(posts.count(), 1)
        posts = NewsPost.get_by_tag('bad-tag')
        self.assertQuerysetEqual(posts, NewsPost.objects.none())

    def test_get_by_strand(self) -> None:
        strand_1 = StrandPageFactory.build()
        strand_2 = StrandPageFactory.build()
        self.home_page.add_child(
            instance=strand_1
        )
        self.home_page.add_child(
            instance=strand_2
        )
        self.news_1.strands.add(strand_1)
        self.news_1.save()
        self.assertQuerysetEqual(
            NewsPost.get_by_strand(None), NewsPost.objects.none())
        self.assertQuerysetEqual(
            NewsPost.get_by_strand('bad strand name'), NewsPost.objects.none()
        )
        self.assertEqual(
            NewsPost.get_by_strand(strand_1).count(),
            1
        )
        self.assertEqual(NewsPost.get_by_strand(strand_1)[0], self.news_1)
        self.assertQuerysetEqual(
            NewsPost.get_by_strand(strand_2), NewsPost.objects.none())


""" View and route Tests"""


class TestBlogIndexPage(TestCase):
    model = BlogIndexPage

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=BlogIndexPageFactory.build(
                title='Blog Index Test'
            )
        )
        self.author_1 = BlogAuthorFactory()
        self.author_2 = BlogAuthorFactory()
        self.blog_index_page = BlogIndexPage.objects.get(
            title='Blog Index Test')
        self.blog_index_page.add_child(
            instance=BlogPostFactory.build(
                author=self.author_1,
            )
        )
        self.post_2 = BlogPostFactory.build(
            author=self.author_2,
            date=date.today(), title='Posted Today'
        )
        self.blog_index_page.add_child(
            instance=self.post_2
        )
        self.post_3 = BlogPostFactory.build(author=self.author_2)
        self.blog_index_page.add_child(
            instance=self.post_3
        )

    def test_posts(self) -> None:
        self.assertEqual(self.blog_index_page.posts.count(), 3)
        # set post live to false
        post_3 = self.blog_index_page.posts[2]
        post_3.live = False
        post_3.save()
        # Should only get 2 posts
        self.assertEqual(self.blog_index_page.posts.count(), 2)
        # First post should be most recent
        self.assertEqual(
            str('Posted Today'), str(self.blog_index_page.posts[0])
        )

    def test_all_posts(self) -> None:
        response = self.client.get(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage(
                'all_posts')
        )
        self.assertEqual(response.status_code, 200)

    def test_tag(self) -> None:
        # add tag to post
        test_tag_label = 'test_tag'
        self.post_2.tags.add(test_tag_label)
        self.post_2.save()
        response = self.client.get(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage(
                'tag',
                kwargs={'tag': 'test_taeg'}
            )
        )
        # Bad tag, we should get nothing
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        page = response.context['posts']
        self.assertEqual(len(page.object_list), 0)
        # Try again, with correct label
        response = self.client.get(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage(
                'tag',
                kwargs={'tag': test_tag_label}
            )
        )
        self.assertEqual(response.status_code, 200)
        page = response.context['posts']
        self.assertEqual(len(page.object_list), 1)
        self.assertEqual(self.post_2.pk, page.object_list[0].pk)

    def test_get_author(self) -> None:
        # Handle author is none
        authors = self.blog_index_page.get_author(None)
        self.assertQuerysetEqual(authors, BlogAuthor.objects.none())
        # Create new author, should have no posts
        new_author = BlogAuthorFactory()
        authors = self.blog_index_page.get_author(new_author.author_slug)
        self.assertQuerysetEqual(authors, BlogAuthor.objects.none())
        # existing author_2, should have 2 posts
        authors = self.blog_index_page.get_author(self.author_2.author_slug)
        self.assertEqual(authors.count(), 2)

    def test_author(self) -> None:
        response = self.client.get(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage(
                'author',
                kwargs={'author': self.author_1.author_slug}
            )
        )
        self.assertEqual(response.status_code, 200)


class TestSearchView(TestCase):
    search_view_name = 'search'
    fixtures = ['tests.json']

    def setUp(self):
        """Set up a mock results class for basic results test"""
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.event_2 = EventFactory.build(
            title='Event Today',
            date_from=date.today()
        )
        self.event_index = EventIndexPageFactory.build(
            title='Event Index Test'
        )
        self.home_page.add_child(
            instance=self.event_index
        )
        self.event_index.add_child(instance=self.event_2)
        self.strand_1 = StrandPageFactory.build()
        self.home_page.add_child(
            instance=self.strand_1
        )
        self.event_2.strands.add(self.strand_1)
        self.event_2.tags.add('test_tag')
        self.event_2.save()
        self.mock_qs = MagicMock(spec=Elasticsearch2SearchResults)
        self.mock_qs.return_value = [self.event_2]
        self.request = RequestFactory().get('/test?q=Lang')

    def test_search_view(self) -> None:
        # Test without q
        response = self.client.get(reverse(self.search_view_name))
        self.assertEqual(response.status_code, 200)

    def test_get_context_data(self) -> None:
        search_view = SearchView()
        search_view.setup(self.request)
        with patch(
                'wagtail.core.models.PageQuerySet.search') as mock_search:
            mock_search.return_value = [self.event_2]
            context = search_view.get_context_data()
        self.assertIn('q', context)
        self.assertIn('results_qs', context)
        self.assertGreater(len(context['results_qs']), 0)
        self.assertIn(self.event_2, context['results_qs'])

    def test_search_results_template(self) -> None:
        # results.paginator.count
        mock_results = MagicMock()
        mock_paginator = create_autospec(Paginator, return_value='fishy')
        mock_paginator.count = 1
        mock_paginator.number = 2
        mock_paginator.num_pages = 3
        mock_paginator.has_previous = True
        mock_paginator.has_next = True
        mock_results.paginator = mock_paginator

        # results = paginator.get_page(page)
        rendered = render_to_string(
            'cms/includes/search_results.html', {
                'request': self.request,
                'results': mock_results,
                'results_qs': self.mock_qs
            })
        self.assertIn(self.event_2.title, rendered)
        self.assertIn("tags plain", rendered)
        # nav links
        self.assertIn('next', rendered)
        self.assertIn('previous', rendered)
        mock_results.paginator = None

        rendered = render_to_string(
            'cms/includes/search_results.html', {
                'request': self.request,
                'results': None,
                'results_qs': self.mock_qs
            })
        self.assertIn("No search term", rendered)
        rendered = render_to_string(
            'cms/includes/search_results.html', {
                'request': self.request,
                'results': None,
                'q': 'test',
                'results_qs': self.mock_qs
            })
        self.assertIn("No results found", rendered)


class TestNewsIndexPage(TestCase):
    model = NewsIndexPage
    index_title = 'News Index Test'
    today_post_title = 'Posted Today'

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=NewsIndexPageFactory.build(
                title=self.index_title
            )
        )
        self.routeable_index_page = NewsIndexPage.objects.get(
            title=self.index_title)
        self.routeable_index_page.add_child(
            instance=NewsPostFactory.build(
            )
        )
        self.post_2 = NewsPostFactory.build(
            title=self.today_post_title,
            date=date.today()
        )
        self.routeable_index_page.add_child(
            instance=self.post_2
        )
        self.post_3 = NewsPostFactory.build()
        self.routeable_index_page.add_child(
            instance=self.post_3
        )

    def test_posts(self) -> None:
        self.assertEqual(self.routeable_index_page.posts.count(), 3)
        # set post live to false
        post_3 = self.routeable_index_page.posts[2]
        post_3.live = False
        post_3.save()
        # Should only get 2 posts
        self.assertEqual(self.routeable_index_page.posts.count(), 2)
        # First post should be most recent
        self.assertEqual(
            str(self.today_post_title), str(self.routeable_index_page.posts[0])
        )

    def test_all_posts(self) -> None:
        response = self.client.get(
            self.routeable_index_page.url
            + self.routeable_index_page.reverse_subpage(
                'all_posts')
        )
        self.assertEqual(response.status_code, 200)

    def test_tag(self):
        test_tag_label = 'test_tag'
        self.post_2.tags.add(test_tag_label)
        self.post_2.save()
        # Bad tag, we should get nothing
        response = self.client.get(
            self.routeable_index_page.url
            + self.routeable_index_page.reverse_subpage(
                'tag',
                kwargs={'tag': 'test_taeg'}
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            self.routeable_index_page.url
            + self.routeable_index_page.reverse_subpage(
                'tag',
                kwargs={'tag': test_tag_label}
            )
        )
        self.assertEqual(response.status_code, 200)


class TestEventIndexPage(TestCase):

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=EventIndexPageFactory.build(
                title='Event Index Test'
            )
        )
        self.event_index = EventIndexPage.objects.get(
            title='Event Index Test'
        )
        self.event_index.add_child(
            instance=EventFactory.build()
        )
        self.event_2 = EventFactory.build(
            title='Event Today',
            date_from=date.today()
        )
        self.event_index.add_child(
            instance=self.event_2
        )

    def test_events(self):
        events = self.event_index.events
        self.assertEqual(events.count(), 2)
        self.assertEqual(events[0].title, 'Event Today')

    def test_all_events(self):
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'all_events')
        )
        self.assertEqual(response.status_code, 200)

    def test_tag(self):
        test_tag_label = 'test_tag'
        self.event_2.tags.add(test_tag_label)
        self.event_2.save()
        # Bad tag, we should get nothing
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'tag',
                kwargs={'tag': 'test_taeg'}
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'tag',
                kwargs={'tag': test_tag_label}
            )
        )
        self.assertEqual(response.status_code, 200)


class TestPastEventIndexPage(TestCase):

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=PastEventIndexPageFactory.build(
                title='Event Index Test'
            )
        )
        self.event_index = PastEventIndexPage.objects.get(
            title='Event Index Test'
        )
        self.event_index.add_child(
            instance=EventFactory.build()
        )
        self.event_2 = EventFactory.build(
            title='Event Today',
            date_from=date.today()
        )
        self.event_index.add_child(
            instance=self.event_2
        )

    def test_events(self):
        events = self.event_index.events
        self.assertEqual(events.count(), 1)

    def test_all_events(self):
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'all_events')
        )
        self.assertEqual(response.status_code, 200)

    def test_tag(self):
        test_tag_label = 'test_tag'
        self.event_2.tags.add(test_tag_label)
        self.event_2.save()
        # Bad tag, we should get nothing
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'tag',
                kwargs={'tag': 'test_taeg'}
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            self.event_index.url
            + self.event_index.reverse_subpage(
                'tag',
                kwargs={'tag': test_tag_label}
            )
        )
        self.assertEqual(response.status_code, 200)


class TestEventTag(TestCase):
    def test_name(self):
        pass


class TestEvent(TestCase):

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=EventIndexPageFactory.build(
                title='Event Index Test'
            )
        )
        self.event_index = EventIndexPage.objects.get(
            title='Event Index Test'
        )
        self.event_1 = EventFactory.build(
            date_from=factory.Faker('past_date')
        )
        self.event_index.add_child(
            instance=self.event_1
        )
        self.event_2 = EventFactory.build(
            title='Event Today',
            date_from=date.today()
        )
        self.event_index.add_child(
            instance=self.event_2
        )
        self.strand_title = 'test_strand'
        self.strand_1 = StrandPageFactory.build(
            title=self.strand_title
        )
        self.home_page.add_child(
            instance=self.strand_1
        )

    def test_get_index_page(self):
        self.assertEqual(self.event_index, self.event_2.get_index_page())

    def test_is_past(self):
        self.assertFalse(self.event_2.is_past)

    def test_get_by_strand(self):
        self.event_2.strands.add(self.strand_1)
        self.event_2.save()
        events = Event.get_by_strand(self.strand_title)
        self.assertEqual(events.count(), 1)
        self.assertIn(self.event_2, events)

    def test_get_by_tag(self):
        test_tag_label = 'test_tag'
        self.event_2.tags.add(test_tag_label)
        self.event_2.save()
        events = Event.get_by_tag(test_tag_label)
        self.assertEqual(events.count(), 1)

    def test_get_past_by_strand(self):
        self.event_1.strands.add(self.strand_1)
        self.event_1.save()
        events = Event.get_past_by_strand(self.strand_title)
        self.assertEqual(events.count(), 1)
        self.assertIn(self.event_1, events)


# todo finish once haystack test added
# class TestRecordIndexPage(TestCase):
#
#     def test_get_context(self):
#         factory = RequestFactory()
#         request = factory.get('/test?selected_facets=first_letter:E')

""" Block function tests """

# class TestSlideBlock(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.author_1 = BlogAuthorFactory()
#         cls.author_2 = BlogAuthorFactory()
#         cls.site_root = create_site_root()
#         cls.home_page = HomePageFactory.build()
#         cls.site_root.add_child(
#             instance=cls.home_page
#         )
#         cls.home_page, cls.blog_index_page = create_blog_index(None)
#         cls.blog_index_page, cls.blog_1 = create_blog_post(
#             cls.blog_index_page, cls.author_1)
#
#     def test_context(self):
#         # Set up carousel page stream field
#         self.home_page.body = nested_form_data({'content': streamfield([
#             ('slides', 'Hello, world'),
#         ])})
#         self.home_page.save()
