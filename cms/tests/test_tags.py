from cms.models.pages import (
    IndexPage
)
from cms.templatetags import cms_tags
from cms.tests.factories import (
    IndexPageFactory
)
from django.test import RequestFactory, TestCase
from wagtail.core.models import Page


class TestPageInSubmenu(TestCase):
    test_page_title = 'Parent Test Page'

    def setUp(self) -> None:
        self.home_page, created = Page.objects.get_or_create(id=2)
        self.home_page.add_child(
            instance=IndexPageFactory.build(
                title='Index Test'
            )
        )
        self.top_page = IndexPage.objects.get(title='Index Test')
        self.top_page.add_child(
            instance=IndexPageFactory.build(
                title=self.test_page_title
            )
        )
        self.top_page.add_child(
            instance=IndexPageFactory.build()
        )
        self.top_page.add_child(
            instance=IndexPageFactory.build()
        )

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
