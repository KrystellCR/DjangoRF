""" Circle permissions classes """

#Django REST Framework
from rest_framework.permissions import BasePermission


#Models
from circles.models import Circle,MemberShip

class IsCircleAdmin(BasePermission):
    """ Alow accesss. only to circle admins """

    def has_object_permission(self, request, view,obj):
        """ Check that the obj and user are te equivalent """
        """ vERIFY USER HAVE MEMEBERSHIP in the obj """
        
        # Inteta tomar el objeto si no se encuentra retorna false 
        try:
            MemberShip.objects.get(
                user=request.user,
                circle=obj,
                is_admin=True,
                is_active=True
            )
        
        except MemberShip.DoesNotExist:
            return False
        
        return True
