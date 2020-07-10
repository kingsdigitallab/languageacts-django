from cms.models.pages import (
    BlogIndexPage, EventIndexPage, HomePage, IndexPage, NewsIndexPage,
    PastEventIndexPage, RichTextPage, StrandPage, _paginate, TagResults,
    BlogPost, BlogAuthor
)
from datetime import date
from django.urls import reverse
from django.test import RequestFactory, TestCase
from wagtail.tests.utils import WagtailPageTests
from cms.tests.factories import (
    BlogIndexPageFactory,
    BlogPostFactory,
    BlogAuthorFactory
)
from wagtail.core.models import Page


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


class TestRichTextPage(WagtailPageTests):
    fixtures = ['tests.json']

    def test_subpage_types(self):
        self.assertAllowedSubpageTypes(RichTextPage, {})


""" View and route Tests"""


def build_blog_index_page() -> BlogIndexPage:
    return BlogIndexPageFactory.build()


def create_blog_post(
        post_title: str = None, live: bool = True) -> BlogPost:
    if post_title:
        return BlogPostFactory(title=post_title, live=live)
    else:
        return BlogPostFactory(live=live)


def create_blog_post_today(post_title='Posted Today') -> BlogPostFactory:
    return BlogPostFactory(date=date.today(), title=post_title)


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
        authors = self.blog_index_page.get_author(new_author)
        self.assertQuerysetEqual(authors, BlogAuthor.objects.none())
        # existing author_2, should have 2 posts
        authors = self.blog_index_page.get_author(self.author_2)
        self.assertEqual(authors.count(), 2)

    def test_author(self) -> None:
        #
        pass


class TestSearchView(TestCase):
    search_view_name = 'search'
    fixtures = ['tests.json']

    def test_search_view(self) -> None:
        # Test without q
        response = self.client.get(reverse(self.search_view_name))
        self.assertEqual(response.status_code, 200)


""" Block function tests """
