'''
Handles routing for the API module
'''

from django.conf.urls import url
from . import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^v1/token/(?P<asset_contract_address>[0-9a-z]+)/(?P<token_id>[0-9]+)$', \
        views.TokenView.as_view(), name='token'),
    url(r'^v1/profile/(?P<address>[0-9a-zA-Z]+)$', \
        views.ProfileView.as_view(), name='profile'),
    url(r'^v1/contract/(?P<address>[0-9a-zA-Z]+)$', \
        views.ContractView.as_view(), name='contract'),
    url(r'^v1/leaderboard$', views.LeaderboardView.as_view(), name='leaderboard'),
    url(r'^v1/featured$', views.FeaturedView.as_view(), name='featured'),

    #TBD: url(r'^v1/search$', views.SearchView.as_view(), name='search'),
]

# Usage Examples

# GET: /api/v1/token/0x0000000000001b84b1cb32787b0d64758d019317/3259539015542658014133428223780909702996875844353040978646893663363117613056
# POST: /api/v1/token/0x0000000000001b84b1cb32787b0d64758d019317/3259539015542658014133428223780909702996875844353040978646893663363117613056 \
    # json body: { "action": "like", "user_email": "test@gmail.com" }
# GET: /api/v1/profile/0xd3e9d60e4e4de615124d5239219f32946d10151d
# GET: /api/v1/contract/0x0000000000001b84b1cb32787b0d64758d019317

# GET: /api/v1/search?q=Lil+Miquela
# GET: /api/v1/featured
# GET: /api/v1/leaderboard
