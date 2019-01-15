from django.db import models
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel


@register_snippet
class BiblioRef(index.Indexed, models.Model):
    author = models.CharField(max_length=256,
                              verbose_name="Author Name")
    year_from = models.IntegerField(verbose_name="Year")
    year_to = models.IntegerField(blank=True, null=True,
                                  verbose_name="End Year (if range)",
                                  help_text="Leave blank if reference spans\
                                             only a single year.")
    link = models.CharField(max_length=2048, blank=True, null=True,
                            verbose_name="Link to source",
                            help_text="URL to any source information.")
    page_from = models.IntegerField(blank=True, null=True,
                                    verbose_name="Start Page (if req.)")
    page_to = models.IntegerField(blank=True, null=True,
                                  verbose_name="End Page (if req.)")
    notes = models.TextField(blank=True, null=True,
                             verbose_name="Internal Notes")

    panels = [
        FieldPanel('author'),
        FieldPanel('year_from'),
        FieldPanel('year_to'),
        FieldPanel('page_from'),
        FieldPanel('page_to'),
        FieldPanel('link'),
        FieldPanel('notes'),

    ]

    search_fields = [
        index.SearchField('author', partial_match=True),
        index.SearchField('year_from', partial_match=True),
        index.SearchField('year_to', partial_match=True),
        index.SearchField('link', partial_match=True),
        index.SearchField('notes', partial_match=True),

    ]

    class Meta:
        verbose_name = "Bibliographic Reference"
        verbose_name_plural = "Bibliographic References"

    def __str__(self):
        name = self.author

        if self.year_to:
            name = '{} ({} - {})'.format(name, self.year_from, self.year_to)
        else:
            name = '{} {}'.format(name, self.year_from)

        if self.page_from and self.page_to:
            name = '{}: p {} - {}'.format(name, self.page_from, self.page_to)
        elif self.page_from:
            name = '{}: p {}'.format(name, self.page_from)

        return name


@register_snippet
class LemmaLanguage(index.Indexed, models.Model):
    name = models.CharField(max_length=128)

    panels = [
        FieldPanel('name'),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        verbose_name = "Lemma Language"
        verbose_name_plural = "Lemma Languages"

    def __str__(self):
        return self.name


@register_snippet
class LemmaPeriod(index.Indexed, models.Model):
    name = models.CharField(max_length=128)

    panels = [
        FieldPanel('name'),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        verbose_name = "Lemma Period"
        verbose_name_plural = "Lemma Periods"

    def __str__(self):
        return self.name
