"""" Circles views """
from django.db.models import Count
#Django REST FRAMEWORKS
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
#Serializers
from circles.serializers import CircleModelSerializer
#models
from users.models import Profile
from circles.models import Circle,MemberShip
#permisssions
from circles.permissions.circles import IsCircleAdmin
#filters
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class CircleViewSet(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):

    serializer_class = CircleModelSerializer 

    lookup_field ='slug_name'
    
    # Filters 
    filter_backends =(SearchFilter,OrderingFilter,DjangoFilterBackend)
    search_fields=('slug_name','name')
    ordering_fields=('rides_offered','rides_taken','name','member_limit')
    
    ordering=('-rides_offered','-rides_taken')
    filter_fields=('verified','is_limited')


    def get_permissions(self):
        """ Assign permissions based on action """
        permissions = [IsAuthenticated]
      
        if self.action in ['update','partial_update']:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions] #instancia cada permiso


    def get_queryset(self):
        """ Restrict list to public-only """
        queryset= Circle.objects.all() #query Base 

        if self.action == 'list': 
            return queryset.filter(is_public=True)
        return queryset
    

    def perform_create(self,serializer): 
	
        circle = serializer.save() 
        user = self.request.user
        profile = user.profile
        
        MemberShip.objects.create( 
            user= user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )
    
