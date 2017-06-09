from django.conf.urls import url
from rest_framework.authtoken import views as auth_views
from . import views
from elections.admin import admin_site

urlpatterns = [
    # Elections, results
    url(r'results/$', views.ResultsCountry.as_view(), name='results_country'),
    url(r'results/voivodeship/(?P<voivodeship_id>[0-9]+)/$', views.ResultsVoivodeship.as_view(), name='results_voivodeships'),
    url(r'results/precinct/(?P<precinct_id>[0-9]+)/$', views.ResultsPrecinct.as_view(), name='results_precinct'),
    url(r'results/borough/(?P<borough_id>[0-9]+)/$', views.ResultsBorough.as_view(), name='results_borough'),
    url(r'results/circuits/(?P<borough_id>[0-9]+)/$', views.ResultsCircuit.as_view(), name='results_circuit'),

    # Elections, related pages
    url(r'pages/voivodeship/(?P<voivodeship_id>[0-9]+)/$', views.PagesVoivodeship.as_view(), name='pages_voivodeship'),
    url(r'pages/precinct/(?P<precinct_id>[0-9]+)/$', views.PagesPrecinct.as_view(), name='pages_precinct'),

    # Elections, all voivodeships
    url(r'voivodeships/$', views.Voivodeship.as_view(), name='voivodeship'),

    # Elections, searching boroughs
    url(r'search/borough$', views.SearchBorough.as_view(), name='search_borough'),

    # Elections, editing circuits
    url(r'edit/circuit/(?P<circuit_id>[0-9]+)/$', views.EditCircuit.as_view(), name='edit_circuit'),

    # Authentication URLs
    url(r'^login/', auth_views.obtain_auth_token),

    url(r'^elections/admin/', admin_site.urls),
]
