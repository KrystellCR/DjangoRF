"""" Circles views """

# DJango REST Framework
from rest_framework import viewsets
#serializers
from .serializer import CircleModelSerializer
# Models
from .models import Circles


class CircleViewSet(viewsets.ModelViewSet):
    """ Circle ViewSet """

    queryset  = Circle.objects.all()
    serializer_class = CircleModelSerializer