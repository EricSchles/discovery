from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

from api import urls as api_urls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mirage.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^api/', include(api_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^results/$', TemplateView.as_view(template_name='pool.html')),
    url(r'^vendor/(?P<vendor_duns>\w+)/$', TemplateView.as_view(template_name='vendor.html')),
    url(r'^results/csv', 'vendor.views.pool_csv', name="pool-csv"),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^vendor/(?P<vendor_duns>\w+)/csv/$', 'vendor.views.vendor_csv', name="vendor-csv"), 
) #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
