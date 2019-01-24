from django.urls import path

from .views.search import SearchView

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),
]
