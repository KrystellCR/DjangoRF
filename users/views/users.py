from django.shortcuts import render
from users.models import Profile
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins,viewsets,status #para mandar http status
from rest_framework.decorators import action 

# Serializers 
from circles.serializers import CircleModelSerializer 
from users.serializers.profile import ProfileModelSerializer
# Models
from circles.models import Circle,MemberShip
# Permisions 
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,

)
from users.permissions import IsAccountOwner 


#Serializers
from users.serializers.users import UsingLoginSerializer,UserModelSerializer,UserSignupSerializer
from users.serializers.users import AccountVerificationSerializer
from rest_framework.authtoken.models import Token
#Class
from rest_framework.views import APIView # importamos la clase

# Models
from users.models import Profile 
from django.contrib.auth.models import User
# Create your views here.
class UserViewSet(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    """ User view set. handle sign up, login and account verify """
    
    queryset = User.objects.filter(is_active=True)
    print(queryset)
    serializer_class = UserModelSerializer
    lookup_field =  'username'#'id'


    def get_permissions(self):
        print ("*******", self.action)
    
        """ Assign permissions based on action """
        if self.action in ['signup','login','verify']:
            permissions = [AllowAny]
        elif self.action in ['retrieve','update','partial_update','profile']:
            print("UPDATE,RETRIEVE,PARTIAL_UPADTE")

            permissions = [IsAuthenticated, IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
      
        return [p() for p in permissions]
    
        
 
    @action(detail=False,methods=['post'])
    def login(self,request): 
        serializer = UsingLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user,token = serializer.save()  
        
        data={
            'user': UserModelSerializer(user).data, 
            'access_token': token
        }
        return Response(data,status=status.HTTP_201_CREATED)


    @action(detail=False,methods=['post'])
    def signup(self,request):
        """ User sign up """
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        user = serializer.save()       
        data={'user': UserModelSerializer(user).data,}
        return Response(data,status=status.HTTP_201_CREATED)



    @action(detail=False,methods=['post'])
    def verify(self,request):   
        serializer = AccountVerificationSerializer(data=request.data)   
        serializer.is_valid(raise_exception=True) 
        serializer.save() 
        data={
            'message':' Ya estas registrado '
        }
        return Response(data,status=status.HTTP_200_OK)


    def retrieve(self,request,*args,**kwargs):
        """ Add extra data to the response """
        #
        print("------------------")
        print("SELFGETOBJET",self.get_object())
        response = super(UserViewSet,self).retrieve(request,*args,**kwargs)
        circles = Circle.objects.filter(
            members=request.user,
            membership__is_active=True) 
        data ={
            'user': response.data,
            'circles':CircleModelSerializer(circles,many=True).data 
        }

        response.data = data
        return response


  
    @action(detail=True, methods=['put','patch'])
    def profile(self,request,*args,**kwargs):
        """ Update profile data """
        user = self.get_object()
        profile = user.profile
        
        partial = request.method == 'PATCH'

        serializer = ProfileModelSerializer(
           profile,
           data= request.data,
           partial=partial 
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
       
        data = UserModelSerializer(user).data
        return Response(data)

    