""" MemberSho serializers """
# utilities
from django.utils import timezone
# Django Rest Framework
from rest_framework import serializers

# Serializers 
from users.serializers import UserModelSerializer 
# Models 
from circles.models import MemberShip,Invitation

class MembershipModelSerializer(serializers.ModelSerializer):
    """ Member model serializer """
    
    user = UserModelSerializer(read_only=True) 
    invited_by = serializers.StringRelatedField() 


    class Meta:
        model = MemberShip
        fields =(
            'user',
            'is_admin','is_active',
            'used_invitations','remaining_invitations',
            'invited_by',
            'rides_taken','rides_offered'
        )
        read_only_fields=(
            'user',
            'used_invitations',
            'invited_by',
            'ride'
        )




class AddMemberSerializer(serializers.Serializer):
    """ Add member serializer 
    Handle the addittion of a new member to a circle.
    Circle object must be provide in the context """

    invitation_code = serializers.CharField(min_length=1)

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self,data):
        """ Verify user isn't already a member """
        print("EN VALIDATE USER")
        import pdb;pdb.set_trace()
        circle = self.context['circle']
        user = data
        import pdb;pdb.set_trace()
        q= MemberShip.objects.filter(circle=circle,user=user)
        if q.exists():
            raise serializers.ValidationError('User is already member of this cirlce')
        

    def validate_invitation_code(self,data):
        """ Verify code exists and  that it is already to the cirlcle """
        import pdb;pdb.set_trace()
        try:
            invitation= Invitation.objects.get(
                code=data,
                circle=self.context['circle'],
                used=False

            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('invalid invitation code')
        self.context['invitation']=invitation
        return data

    def validate(self,data):
        """ Verify cirlce is capable of acepting a new member"""
        import pdb;pdb.set_trace()
        circle = self.context['circle']
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializersWS.ValidationError('Circle has reached its memberberlimit')
        return data

    def create(self,data):
        """ Create new circle member """
        # Se sobre escribe el metodo create porque se tiene que agregar el invited_by y updatear en la tabla membership
        import pdb;pdb.set_trace()
        circle= self.context['circle']
        invitation = self.context['invitation']
        user = self.context['request'].user #data ['user']

        now= timezone.now()

        import pdb;pdb.set_trace()
        # Member creation
        member = MemberShip.objects.create(
            user = user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by,
            is_active=True
        )
        #Udate invitation
        invitation.used_by = user
        invitation.used=True
        invitation.used_at = now
        invitation.save()

        import pdb;pdb.set_trace()
        # Update issued data
        issuer = MemberShip.objects.get(user=invitation.issued_by,circle=circle)
        issuer.used_invitations+=1
        issuer.remaining_invitations-=1

        return member 