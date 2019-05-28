from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from wagtail.admin.edit_handlers import FieldPanel

@register_snippet
class LemmaLanguage(index.Indexed, models.Model):
    name = models.CharField(max_length=128)
    orderno = models.IntegerField(default=0)

    panels = [
        FieldPanel('name'),
        FieldPanel('orderno'),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        verbose_name = "Lemma Language"
        verbose_name_plural = "Lemma Languages"

        ordering = ['orderno']

    def __str__(self):
        return self.name


@register_snippet
class POSLabel(index.Indexed, models.Model):
    name = models.CharField(max_length=256)

    panels = [
        FieldPanel('name'),
    ]

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        verbose_name = "Eagle POS Label"
        verbose_name_plural = "Eagle POS Labels"

    def __str__(self):
        return self.name
