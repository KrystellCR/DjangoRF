""" Circles membeships views """

#DJango REST Framework
from rest_framework import mixins,viewsets,status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action 
from rest_framework.response import Response
#MODELS
from circles.models import Circle,MemberShip,Invitation

#permissions 
from rest_framework.permissions import IsAuthenticated
from circles.permissions.memberships import isActiveCircleMember,isSelfMember
#Serializers
from circles.serializers.memberships import MembershipModelSerializer,AddMemberSerializer

class MembershipViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin, 
                        viewsets.GenericViewSet):
    """ Circle membership viewSet """

    serializer_class= MembershipModelSerializer
    
    # Metodo qeu siempre se manda a llamar ya que maneja las peticiones 
    def dispatch(self,request,*args,**kwargs):
        """ Verify tha the circle existis """
        slug_name = kwargs ['slug_name']
        self.circle = get_object_or_404( Circle, slug_name=slug_name )
        return super(MembershipViewSet,self).dispatch(request,*args,**kwargs)


    def get_permissions(self):
        """ Assign permission based on action """
        permissions = [IsAuthenticated]
        if self.action !='create':
            permissions.append(isActiveCircleMember)
        if self.action in ['invitations']:         
            permissions.append(isSelfMember)      
        return [p() for p in permissions ]

    def get_queryset(self):
        """ Return circle"""
        return MemberShip.objects.filter(
            circle = self.circle,
            #user = self.request.user,
            is_active = True
        )

    
    def get_object(self): 
        """ Return the circle memeber by using the user's username """
        return get_object_or_404(
            MemberShip,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )

    def perform_destroy(self,instance):
        """ Disable memembership este metodo es para el borrado """
        instance.is_active=False
        instance.save()


    @action(detail=True,methods=['get']) # Es un list 
    def invitations(self,request,*args,**kwargs):
        """ Retrieve a member's invitations breakdown.
        
        will return a list containing all the members that have
        used its invitations and another lit containing the 
        invitations that haven't being used yet
        
        genera todos lso codigos que un usuari tiene para poder distrubir a sus amigos
        y decir a LOS USUARIOS  quien ha invitado 
         """

        print ("self",self.get_object(),"request",self.request.user )     
        # Primero vemos a quien ya invito este miembro del circulo a otros usuarios para ser miembros 
        invited_members= MemberShip.objects.filter(
            circle=self.circle,
            invited_by=request.user,
            is_active=True
        )

        """ ahora vemos los codigos disponibles para usar """
        #Ver las invitaciones hechas por el usuario que no se han usado 
        unused_invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user, #creadas por 
            used=False 
        ).values_list('code')

        
        member= self.get_object()
        diff = member.remaining_invitations - len(unused_invitations)     
       
     
        invitations = [x[0] for x in unused_invitations]

        
        for i in range(0,diff):
            invitations.append(
               
                Invitation.objects.create(
                    issued_by=request.user,
                    circle=self.circle                

                ).code 
            )
        
        # Diccionario de datos final, 
        data={
            'used_invitations':MembershipModelSerializer(invited_members,many=True).data,
            'invitations': invitations
        }
        return Response(data)


    def create(self,request,*args,**kwargs):
        """ Handle member creation from invitation code """
        
        serializer = AddMemberSerializer(
            data=request.data,
            
            context={'circle':self.circle,'request':request}
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

      
        data = self.get_serializer(member).data
        return Response(data,status=status.HTTP_201_CREATED)

