from django.conf import settings
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from wagtail.core.models import Page


class SearchView(TemplateView):
    template_name = ('cms/search_results_page.html')

    def get_context_data(self, **kwargs):
        context = super(SearchView,
                        self).get_context_data(**kwargs)

        if 'q' in self.request.GET:
            q = self.request.GET['q']

            pages = Page.objects.all()
            results_qs = pages.search(q)

            paginator = Paginator(results_qs, settings.ITEMS_PER_PAGE)

            if 'page' in self.request.GET:
                page = int(self.request.GET['page'])
            else:
                page = 1

            results = paginator.get_page(page)

            context['q'] = q
            context['results'] = results
            context['results_qs'] = results_qs[results.start_index(
            ) - 1:(results.start_index() - 1) + settings.ITEMS_PER_PAGE]
        return context
