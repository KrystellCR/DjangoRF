"""Ride ViewSet """

#Django RESTFRAME work 
from rest_framework import viewsets, mixins,status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action 
#permissions
from rest_framework.permissions import IsAuthenticated
#from djangoAPIREST.circles.permissions.memberships import isActiveCircleMember,isSelfMember
from circles.permissions.memberships import *
from rides.permissions.rides import IsRideOwner,IsNotRideOwner,IsMemberRide
#utilites
from datetime import timedelta
from django.utils import timezone

#Serializer
from rides.serializers import (
    CreateRideSerialier,
    RideModelSerializer,
    JoinRideSerializer,
    EndRideSerializer,
    SocoreRideSerializer
)

#filters
from rest_framework.filters import SearchFilter,OrderingFilter


#Models 
from circles.models import Circle,MemberShip

class RideViewSet(mixins.CreateModelMixin,
                mixins.ListModelMixin,
                mixins.UpdateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """ Ride ViewSet"""

    serializer_class= CreateRideSerialier

    filter_backends=(SearchFilter,OrderingFilter)
    # ordering es por default 
    orderings=('departure_date','arrival_date','avaible_seats')
    ordering_fields=('departure_date','arrival_date','avaible_seats')
    search_fields=('departure_location','arrival_location')

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *args, **kwargs)



    def get_permissions(self):
        permissions=[IsAuthenticated,isActiveCircleMember]
        if self.action in ['update','partial_update','finish']:
            permissions.append(IsRideOwner)

        elif self.action == 'join':
            permissions.append(IsNotRideOwner)
        
        elif self.action=='scoreRide':
            permissions.append(IsNotRideOwner)
            permissions.append(IsMemberRide) 

        return [p() for p in permissions]



    def get_serializer_context(self):
        """ Add circle to serializer context """

        context = super(RideViewSet,self).get_serializer_context()
        context['circle']= self.circle
        return context 


    def get_serializer_class(self):
        """ Return serializer based on action """
        if self.action == 'create':
            return CreateRideSerialier
        if self.action=='join': 
            return JoinRideSerializer
        if self.action=='finish':
            return EndRideSerializer
        if self.action=='scoreRide':
            return SocoreRideSerializer
        return RideModelSerializer


    def get_queryset(self):
        """ Return active circles rides """
        if self.action!='finish':
            offset=timezone.now() + timedelta(minutes=10) 
            return self.circle.rides_set.filter(
                departure_date__gte=offset,
                is_active=True,
                avaible_seats__gte=1
            )

        else:
            return self.circle.rides_set.all()


    
    @action(detail=True,methods=['post'])
    def join(self,request,*args,**kwargs):
        """ Add requesting user to ride """
        ride = self.get_object()
        serializer_class= self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'passanger': request.user.pk}, 
            context={'ride':ride,'circle':self.circle},
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        ride =serializer.save()
        # mostramos el ride de regreso 
        data= RideModelSerializer(ride).data
        return Response(data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['post'])
    def finish(self,request,*args,**kwargs):
        """ Call by owners to finish a ride """
        ride = self.get_object()
        serializer_class= self.get_serializer_class()
        # hacemos un update parcial
        serializer= serializer_class(
            ride,
            data={'is_active':False,'current_time':timezone.now()},
            context=self.get_serializer_context(),
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride= serializer.save()
        data=RideModelSerializer(ride).data
        return Response(data,status=status.HTTP_200_OK)


    @action(detail=True,methods=['post'])
    def scoreRide(self,request,*args,**kwargs):
        """ scored raide """
        ride = self.get_object()
        serializer_class= self.get_serializer_class()
        serializer= serializer_class(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        score=serializer.save()
        data = self.get_serializer(score).data
        return Response(data,status=status.HTTP_200_OK)
