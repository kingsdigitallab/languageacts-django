from django.conf import settings
from django.urls import include, re_path, path
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
# from wagtail.search.urls import frontend as wagtailsearch_frontend_urls TODO

from kdl_ldap.signal_handlers import \
    register_signal_handlers as kdl_ldap_register_signal_hadlers

kdl_ldap_register_signal_hadlers()

admin.autodiscover()


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('digger/', include('activecollab_digger.urls')),
]

# -----------------------------------------------------------------------------
# Wagtail CMS
# -----------------------------------------------------------------------------

urlpatterns += [
    re_path('wagtail/', include(wagtailadmin_urls)),
    re_path('documents/', include(wagtaildocs_urls)),
    # re_path(r'^search/', include(wagtailsearch_frontend_urls)), TODO

    re_path('', include(wagtail_urls)),
]

# -----------------------------------------------------------------------------
# Django Debug Toolbar URLS
# -----------------------------------------------------------------------------
try:
    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += [
            re_path('__debug__/',
                    include(debug_toolbar.urls)),
        ]

except ImportError:
    pass

# -----------------------------------------------------------------------------
# Static file DEBUGGING
# -----------------------------------------------------------------------------
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import os.path

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL + 'images/',
                          document_root=os.path.join(settings.MEDIA_ROOT,
                                                     'images'))
