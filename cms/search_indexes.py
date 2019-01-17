from haystack import indexes

from .models import (RecordPage, RecordEntry)


class RecordEntryIndex(indexes.SearchIndex, indexes.Indexable):
    # Model attributes
    title = indexes.CharField(model_attr='title', null=True)

    # Text search
    text = indexes.CharField(document=True, use_template=True,
                             template_name='cms/search_indexes/'
                             'recordentry_text.txt')

    # Prepared values
    first_attest_year = indexes.IntegerField(
        faceted=False,
        null=True)

    language = indexes.CharField(
        faceted=False,
        null=True)

    period = indexes.CharField(
        faceted=False,
        null=True)

    word_type = indexes.MultiValueField(
        faceted=False,
        null=True)

    def get_model(self):
        return RecordEntry

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_first_attest_year(self, obj):
        if obj.specific.first_attest_year:
            return obj.specific.first_attest_year
        else:
            return None

    def prepare_language(self, obj):
        return obj.specific.language.name if obj.specific.language else None

    def prepare_period(self, obj):
        return obj.specific.period.name if obj.specific.period else None

    def prepare_word_type(self, obj):
        if obj.specific.word_types:
            return [word_type.name for word_type in obj.specific.word_types]
        else:
            return None


class RecordPageIndex(indexes.SearchIndex, indexes.Indexable):
    # Model Attributes
    title = indexes.CharField(model_attr='title', null=True)

    # Text search
    text = indexes.CharField(document=True, use_template=True,
                             template_name='cms/search_indexes/'
                             'recordpage_text.txt')

    # Prepared values
    first_attest_year = indexes.MultiValueField(
        faceted=True,
        null=True)

    first_letter = indexes.CharField(
        faceted=True,
        null=True)

    language = indexes.MultiValueField(
        faceted=True,
        null=True)

    period = indexes.MultiValueField(
        faceted=True,
        null=True)

    word_type = indexes.MultiValueField(
        faceted=True,
        null=True)

    def get_model(self):
        return RecordPage

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_first_attest_year(self, obj):
        return [entry.specific.first_attest_year for entry in
                obj.get_children() if entry.specific.first_attest_year
                is not None]

    def prepare_first_letter(self, obj):
        return obj.title.upper()[0] if obj.title else None

    def prepare_language(self, obj):
        return [entry.specific.language.name for entry in
                obj.get_children() if entry.specific.language is not None]

    def prepare_period(self, obj):
        return [entry.specific.period.name for entry in
                obj.get_children() if entry.specific.period is not None]

    def prepare_word_type(self, obj):
        word_types = []

        for page in obj.get_children():
            if page.specific.word_types:
                word_types = word_types + [word_type.name for word_type in
                                           page.specific.word_types]

        return word_types if len(word_types) else None
