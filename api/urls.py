'''
Handles routing for the API module
'''

from django.conf.urls import url
from . import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^item/(?P<token>[0-9a-z]+)$', views.ItemView.as_view(), name='item'),
    url(r'^search$', views.SearchView.as_view(), name='search'),
    url(r'^featured$', views.FeaturedView.as_view(), name='featured'),
    url(r'^leaderboard$', views.LeaderboardView.as_view(), name='leaderboard'),
    url(r'^profile/(?P<username_or_address>[0-9a-zA-Z]+)$', \
        views.ProfileView.as_view(), name='profile'),
]

# Usage Examples

# GET: /api/item/0x752aa32a2cc49aed842874326379ea1f95b1cbe6
# POST: /api/item/0x752aa32a2cc49aed842874326379ea1f95b1cbe6 \
    # json body: { "action": "like", "user_id": "1234567" }
# GET: /api/search?q=Lil+Miquela
# GET: /api/featured
# GET: /api/leaderboard
# GET: /api/profile/0xd3e9d60e4e4de615124d5239219f32946d10151d
