from users.models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate,password_validation
from django.core.mail import send_mail,EmailMultiAlternatives
from django.utils import timezone
from django.conf import settings 
import jwt

from django.template.loader import render_to_string

#utilities
from datetime import timedelta 

#models 
from django.contrib.auth.models import User
#importamos el modelo del token
from rest_framework.authtoken.models import Token

# serializer
from users.serializers.profile import ProfileModelSerializer


class UserModelSerializer(serializers.ModelSerializer):
  
       
    profile = ProfileModelSerializer(read_only=True)
    print(profile)
    class Meta:
        model = User
       
        profile = ProfileModelSerializer(read_only=True) 

        fields = [ 'username',
            'email',
            'first_name',
            'profile'# Agregamos el campo del modelo profile 
             ]



class UsingLoginSerializer(serializers.Serializer):
    """Maneja el longin request data"""
    username=serializers.CharField()
    password= serializers.CharField(min_length=2,max_length=200)
    
 
    def validate(self,data):
        user = authenticate(username=data['username'],password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credenciales')

        if not user.profile.is_verified:
            raise serializers.ValidationError('Account is not active yet') #Lanzamos este error 

        self.context['user'] = user 
        return data

    def create(self,data):
        """ Genera or retrieve new Token """
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
         validators=[

            UniqueValidator(queryset=User.objects.all())
                  ]
            )
    username = serializers.CharField(
        max_length=20,
         validators=[
            # Valida que sea unico dentro de este modelo
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    password= serializers.CharField(max_length=20)
    password_confirmation = serializers.CharField(max_length=20)
 
    def validate(self,data):
        passwd = data['password']
        pass_conf=data['password_confirmation']
        if passwd != pass_conf:
            raise serializers.ValidationError(' las password no coinciden')
            password_validation.validate_password(passwd)
        return data

    def create(self,data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        Profile.objects.create(user=user) #En caso de tener un modelo de user extendido en otra bd 
        self.send_confirmation_email(user)
        return user 

    def send_confirmation_email(self,user):
        
        verification_token = self.gen_verification_token(user)
        subject="Welcome @{} verify our count".format(user.username)
        from_email='Hola <cristel@quierotrabajo.co>'
        content = render_to_string(
            'emails/account_verification.html',
            {'token':verification_token, 'user':user}
        )
        msg = EmailMultiAlternatives(subject,content,from_email,[user.email])
        msg.attach_alternative(content,"text/html")
        msg.send()
        print("sending email")

    def gen_verification_token(self,user):
        """ create a jwt token that el usuario puede usar para verificar su cuenta """
        exp_date = timezone.now()+ timedelta(days=3) #dia actual +3
        payload ={ # datos 
            'user':user.username,
            'exp': int(exp_date.timestamp()), 
            'type': 'email_confirmation' 
                                      
        }
        token = jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')

        return token.decode() 
    




class AccountVerificationSerializer(serializers.Serializer):
    """ Account verification serializer """
    token = serializers.CharField()
    # Vamos a validar el campo  token 

    def validate_token(self,data):
        """ Verify token is valid """     
        try:
            payload = jwt.decode(data,settings.SECRET_KEY,algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verificacion link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token type')
        
        self.context['payload'] = payload
        return data 


    def save(self):
        """ Update users verified status """   
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        print("PARA user",user)
        user.profile.is_verified = True
        user.profile.save()
