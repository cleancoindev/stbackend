'''
Handles routing for the API module
'''
from django.conf.urls import url
from . import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^search$', views.SearchView.as_view(), name='search'),
    url(r'^featured$', views.FeaturedView.as_view(), name='featured'),
    url(r'^leaderboard$', views.LeaderboardView.as_view(), name='leaderboard'),
    url(r'^item$', views.ItemView.as_view(), name='item'),


    url(r'^test$', views.TestView.as_view(), name='test'),
]
