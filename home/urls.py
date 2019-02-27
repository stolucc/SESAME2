from django.conf.urls import url
from home.views import HomeView

from . import views

urlpatterns = [

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^publish_call$', views.pub, name='pub'),
    url(r'^call_view$', views.get_call_view, name='call_view'),
    url(r'^my_calls$', views.get_my_calls, name='my_calls'),
    url(r'^centers$', views.view_center, name='view_center'),
    url(r'^centers/create_center$', views.create_center, name='create_center'),

]
