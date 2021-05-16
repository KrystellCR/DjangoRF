
from  users.views import *
#from users.views import *
from django.urls import path

from django.urls import include,path 

#Django RESTFREmework
from rest_framework.routers import DefaultRouter

from users.views import users as user_views 
router = DefaultRouter()
router.register(r'users',user_views.UserViewSet,basename='users')

urlpatterns=[
   path('',include(router.urls))
]
