from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^RiotCrew/', include('RiotCrew.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^team/(?P<number>\d+)$', 'Profiling.views.ShowTeam'),
    (r'^viewTeams$', 'Profiling.views.viewDefaultTeam'),
    (r'^uploadPhoto$', 'Profiling.views.uploadPhoto'),
    (r'^$', 'Profiling.views.root'),
    (r'^Admin$', 'Profiling.views.admin'),
    (r'^Admin/pdf$', 'Profiling.views.team_pdf'),
    (r'^Admin/observer$', 'Profiling.views.add_observer'),
    (r'^observations/match$', 'Profiling.views.NewMatchObservation'),
    (r'^observations/practice$', 'Profiling.views.NewPracticeObservation'),
    (r'^ranking$', 'Profiling.views.ranking'),
    (r'^bulk_import$', 'Profiling.views.bulk_import'),
    (r'^observer_import$', 'Profiling.views.observer_import'),
    (r'^content/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': settings.MEDIA_ROOT}),
)
