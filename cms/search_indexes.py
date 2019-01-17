from haystack import indexes

from .models import (RecordPage, RecordEntry)


class RecordEntryIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title', null=True)
    text = indexes.CharField(document=True, use_template=True,
                             template_name='cms/search_indexes/'
                             'recordentry_text.txt')

    def get_model(self):
        return RecordEntry

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class RecordPageIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title', null=True)
    text = indexes.CharField(document=True, use_template=True,
                             template_name='cms/search_indexes/'
                             'recordpage_text.txt')

    def get_model(self):
        return RecordPage

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
