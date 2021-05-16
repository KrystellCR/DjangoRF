""" circles permissions clasess """
  
# Django REST framework 
from rest_framework.permissions import BasePermission

#models 
from circles.models import MemberShip


class isActiveCircleMember(BasePermission):
    """ Aloow access only to circle members 
    Expect that the views implementing this permissions
    have a circle atribute assigned.
    Esperamso que las vistas que hereden de esto ya tengan la propiedad circulo
    
    """
    
    def has_permission(self,request,view):
        """ Verify user is an actie member of the circle """
        try:
            MemberShip.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True
            )
        except MemberShip.DoesNotExist:
            return False 

        return True


class isSelfMember(BasePermission): 
    """ Allo access only to member owners """

    def has_permission(self, request, view):  
        """ Let object permission grant access """
        obj = view.get_object()
        return self.has_object_permission(request,view,obj)

    def has_object_permission(self,request,view,obj):
        """ Allow accesss only if member is owned by the requesting user """
        return request.user == obj.user 


def hola():
    print("hola")
    

    