from django.urls import include, path

# Recibe un viewSet 
from rest_framework.routers import DefaultRouter

#DjangoRF nos da routers que recibe un viewset y genera los paths que necesitas

#views
from .views import circles as circles_views 
from .views import memberships as membership_views

router = DefaultRouter()
router.register(r'circles',circles_views.CircleViewSet,basename='circle')


router.register(
    r'circles/(?P<slug_name>[-a-zA-Z0-0_]*)/members',
    membership_views.MembershipViewSet,
    basename='membership'
)


urlpatterns = [
    path('',include(router.urls))
]