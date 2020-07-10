# EventIndexPage, HomePage, IndexPage, NewsIndexPage,
import factory
from cms.models.pages import (
    BlogIndexPage, BlogPost, BlogAuthor
)


class BlogAuthorFactory(factory.DjangoModelFactory):
    author_name = factory.Faker('name')

    class Meta:
        model = BlogAuthor


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
