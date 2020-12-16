'''
Handles routing for the API module
'''
from django.conf.urls import url
from . import views

app_name = 'api'

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^test$', views.TestView.as_view(), name='test'),
]
