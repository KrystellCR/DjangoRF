from django.urls import include, path

# Recibe un viewSet 
from rest_framework.routers import DefaultRouter

#DjangoRF nos da routers que recibe un viewset y genera los paths que necesitas

#views
from .views import rides as ride_views 

router = DefaultRouter()

router.register(
    r'circles/(?P<slug_name>[-a-zA-Z0-0_]*)/rides',
    ride_views.RideViewSet,
    basename='ride'
)


urlpatterns = [
    path('',include(router.urls))
]