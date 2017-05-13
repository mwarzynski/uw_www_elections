from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Elections URLs
    url(r'voivodeship/(?P<voivodeship_id>[0-9]+)/$', views.Voivodeship.as_view(), name='voivodeship'),
    url(r'precinct/(?P<precinct_id>[0-9]+)/$', views.Precinct.as_view(), name='precinct'),
    url(r'borough/(?P<borough_id>[0-9]+)$', views.Borough.as_view(), name='borough'),
    url(r'borough/search', views.BoroughSearch.as_view(), name='borough_search'),
    url(r'circuit/(?P<circuit_id>[0-9]+)$', views.CircuitEdit.as_view(), name='circuit_edit'),

    # Authentication URLs
    url(r'login/$', auth_views.login, kwargs={'redirect_authenticated_user': True}, name='login'),
    url(r'logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
