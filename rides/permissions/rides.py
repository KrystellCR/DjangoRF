""" Rides permissions """

# Django RESTFRamework
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """ Verify requesting user is the ride created """

    def has_object_permissions(self,requet,view,obj):
        return request.user== obj.offered_by
        

class IsNotRideOwner(BasePermission):
    
    def has_permission(self, request, view):  
        """ Let object permission grant access """
        obj = view.get_object()
        return self.has_object_permission(request,view,obj)

    def has_object_permission(self,request,view,obj):
        """ Allow accesss only if NOT member is owned by the requesting user """
        return request.user != obj.offered_by 


class IsMemberRide(BasePermission):
    def has_permission(self, request, view):  
        """ Let object permission grant access """
        obj = view.get_object()
        return self.has_object_permission(request,view,obj)

    def has_object_permission(self,request,view,obj):
        """ Allow accesss only if member is owned by the requesting user """
        print("en has_object_permission")
        return obj.passangers.filter(pk=request.user.pk).exists()