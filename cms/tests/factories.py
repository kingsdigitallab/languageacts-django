# EventIndexPage, HomePage, IndexPage, NewsIndexPage,
import factory
from cms.models.pages import (
    BlogIndexPage, BlogPost, BlogAuthor,
    NewsIndexPage, NewsPost, StrandPage,
)


class BlogAuthorFactory(factory.DjangoModelFactory):
    author_name = factory.Faker('name')

    class Meta:
        model = BlogAuthor


class StrandPageFactory(factory.DjangoModelFactory):
    title = factory.Faker('sentence', nb_words=4)

    class Meta:
        model = StrandPage


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
    date = factory.Faker('date')
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
    date = factory.Faker('date')
    live = True
    depth = 3

    class Meta:
        model = NewsPost
        django_get_or_create = ["title", "path", "depth"]
