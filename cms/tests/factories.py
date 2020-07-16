# EventIndexPage, HomePage, IndexPage, NewsIndexPage,
import factory
from cms.models.pages import (
    BlogIndexPage, BlogPost, BlogAuthor, RichTextPage,
    NewsIndexPage, NewsPost, StrandPage, IndexPage,
    EventIndexPage, Event
)


class BlogAuthorFactory(factory.DjangoModelFactory):
    author_name = factory.Faker('name')

    class Meta:
        model = BlogAuthor


class StrandPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)

    class Meta:
        model = StrandPage


class IndexPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)

    class Meta:
        model = IndexPage


class EventIndexPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = "00010009"
    depth = 2

    class Meta:
        model = EventIndexPage


class EventFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = factory.Sequence(lambda n: "00010009%04d" % n)
    # By default we make events in the past
    date_from = factory.Faker('past_date')
    time = factory.Faker('time')
    location = factory.Faker('city')
    live = True
    depth = 3

    class Meta:
        model = Event
        django_get_or_create = ["title", "path", "depth"]


class RichTextPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = "00010009"
    depth = 3

    class Meta:
        model = RichTextPage


class BlogIndexPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = "00010009"
    depth = 2

    class Meta:
        model = BlogIndexPage
        django_get_or_create = ["title", "path", "depth"]


class BlogPostFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = factory.Sequence(lambda n: "00010009%04d" % n)
    author = factory.SubFactory(BlogAuthorFactory)
    date = factory.Faker('past_date')
    live = True
    depth = 3

    class Meta:
        model = BlogPost
        django_get_or_create = ["title", "path", "depth"]


class NewsIndexPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)

    path = "00010009"
    depth = 2

    class Meta:
        model = NewsIndexPage
        django_get_or_create = ["title", "path", "depth"]


class NewsPostFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)
    path = factory.Sequence(lambda n: "00010009%04d" % n)
    date = factory.Faker('past_date')
    live = True
    depth = 3

    class Meta:
        model = NewsPost
        django_get_or_create = ["title", "path", "depth"]


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('name')

    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)
