from django.conf.urls import patterns, url

urlpatterns = patterns(
    'ajax_upload.views',
    url(r'^$', 'upload', name='ajax-upload'),
    url(r'^preview/(?P<param>.+)', 'preview', name='preview-url'),
)
