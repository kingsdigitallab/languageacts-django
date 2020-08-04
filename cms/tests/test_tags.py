from cms.models.pages import (
    IndexPage
)
from cms.templatetags import cms_tags
from cms.tests.factories import (
    IndexPageFactory, BlogIndexPageFactory, BlogPostFactory, BlogAuthorFactory
)
from django.test import RequestFactory, TestCase
from wagtail.core.models import Page


class CMSTagsTestCase(TestCase):
    """Helper class to store wagtail content creation for easier tag
    testing"""
    test_page_title = 'Parent Test Page'

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.top_page = IndexPageFactory.build(
            title='Index Test',
            live=True
        )
        self.top_page.show_in_menus = True
        self.home_page.add_child(
            instance=self.top_page
        )

        self.top_page.add_child(
            instance=IndexPageFactory.build(
                title=self.test_page_title,
                live=True
            )
        )
        self.page_1 = IndexPageFactory.build(live=True)
        self.page_1.show_in_menus = True
        self.top_page.add_child(
            instance=self.page_1
        )
        self.top_page.add_child(
            instance=IndexPageFactory.build(live=True),
        )


class TestPageInSubmenu(CMSTagsTestCase):

    def test_page_in_submenu(self) -> None:
        page = IndexPage.objects.get(title=self.test_page_title)
        # pass bad params make sure it handles it
        self.assertFalse(cms_tags.page_in_submenu(page, None))
        self.assertFalse(cms_tags.page_in_submenu(None, self.top_page))
        # Find page in submenu only if it's toggled in menu
        # nope
        self.assertFalse(cms_tags.page_in_submenu(page, self.top_page))
        # now
        page.show_in_menus = True
        page.save()
        self.assertTrue(cms_tags.page_in_submenu(page, self.top_page))


class TestGetRequestParameters(TestCase):

    def test_get_request_parameters(self) -> None:
        factory = RequestFactory()
        get_string = "page=1&stuff=1"
        request = factory.get('/test?' + get_string)
        context = {'request': request}
        new_get_string = cms_tags.get_request_parameters(context)
        self.assertTrue('stuff=1' in new_get_string)
        self.assertTrue('page=1' in new_get_string)
        self.assertEqual(
            cms_tags.get_request_parameters(context, 'page'), '&stuff=1')


class TestShowChildrenInMenu(CMSTagsTestCase):

    def setUp(self) -> None:
        super().setUp()
        # Add a blog whose children we shouldn't see
        self.blog_index = BlogIndexPageFactory.build(
            title=self.test_page_title,
            live=True
        )
        self.top_page.add_child(
            instance=self.blog_index
        )
        self.blog_1 = BlogPostFactory.build(
            author=BlogAuthorFactory(),
            live=True
        )
        self.blog_index.add_child(
            instance=self.blog_1,
        )

    def test_show_children_show_in_menus(self):
        self.top_page.show_in_menus = True
        self.top_page.save()
        self.page_1.show_in_menus = True
        self.page_1.save()
        tag_dict = cms_tags.show_children_in_menu(self.top_page)
        self.assertIn('show_children', tag_dict)
        self.assertIn('children', tag_dict)
        self.assertTrue(tag_dict['show_children'])
        self.assertGreater(tag_dict['children'].count(), 0)
        tag_dict = cms_tags.show_children_in_menu(self.blog_index)
        # children for blogs shouldn't be displayed
        self.assertFalse(tag_dict['show_children'])
        self.assertTemplateUsed('cms/tags/show_children_show_in_menus.html')
