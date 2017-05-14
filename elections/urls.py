from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Elections results URLs
    url(r'results/$', views.ResultsCountry.as_view(), name='results_country'),
    url(r'results/voivodeship/(?P<voivodeship_id>[0-9]+)/$', views.ResultsVoivodeship.as_view(), name='results_voivodeships'),
    url(r'results/precinct/(?P<precinct_id>[0-9]+)/$', views.ResultsPrecinct.as_view(), name='results_precinct'),
    url(r'results/borough/(?P<borough_id>[0-9]+)/$', views.ResultsBorough.as_view(), name='results_borough'),
    url(r'results/circuits/(?P<borough_id>[0-9]+)/$', views.ResultsCircuit.as_view(), name='results_circuit'),

    # Elections pages URLs
    url(r'pages/voivodeship/(?P<voivodeship_id>[0-9]+)/$', views.PagesVoivodeship.as_view(), name='pages_voivodeship'),
    url(r'pages/precinct/(?P<precinct_id>[0-9]+)/$', views.PagesPrecinct.as_view(), name='pages_precinct'),


    url(r'voivodeships/$', views.Voivodeship.as_view(), name='voivodeship'),
    url(r'precinct/(?P<precinct_id>[0-9]+)/$', views.Precinct.as_view(), name='precinct'),
    url(r'borough/(?P<borough_id>[0-9]+)$', views.Borough.as_view(), name='borough'),
    url(r'borough/search', views.BoroughSearch.as_view(), name='borough_search'),
    url(r'circuit/(?P<circuit_id>[0-9]+)/edit$', views.CircuitEdit.as_view(), name='circuit_edit'),

    # Authentication URLs
    url(r'login/$', auth_views.login, kwargs={'redirect_authenticated_user': True}, name='login'),
    url(r'logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
