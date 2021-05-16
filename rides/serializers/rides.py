""" Rides serializers """

#DJango rest Framework
from rest_framework import serializers
from rest_framework.decorators import action 

#models
from rides.models import *
from circles.models import *
from django.contrib.auth.models import User

#Serializers 
from users.serializers import UserModelSerializer
#utilites
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg

class RideModelSerializer(serializers.ModelSerializer):
    """ Ride model serializer """
    offered_by= UserModelSerializer(read_only=True)
    offered_in=serializers.StringRelatedField()

    passangers= UserModelSerializer(read_only=True,many=True)

    class Meta:
        model=Rides
        fields= '__all__' #Dar todos los campos
        read_only_fields=(
            'offered_by',
            'offered_in'
        )

    
    def update(self,instance,data):
        """ Allow updates only before departure date """
        now=timezone.now()
        if instance.departure_date<=now:
            raise serializers.ValidationError('Ongoing rides cannot be modifed')
        return super(RideModelSerializer,self).update(instance,data)

        

class CreateRideSerialier(serializers.ModelSerializer):
    """ Create ride serializer """
    offered_by=serializers.HiddenField(default=serializers.CurrentUserDefault())
    avaible_seats= serializers.IntegerField(min_value=1,max_value=15)

    class Meta:
        """ meta class """
        model = Rides
        exclude=('offered_in','passangers','rating','is_active')
    
    def validate_departure_date(self,data):
        """ Verify date is not in the past """
        print(data)
        min_date = timezone.now()+ timedelta(minutes=10)
        if data <=min_date:
            raise serializers.ValidationError(
                'Departure time must be at least pass the next 20 minutes window'
            )
        return data

    def validate(self,data):
        """ Validate 
        Verify that the person who offers the ride is member
        and also the same user making the request """
        if self.context['request'].user!=data['offered_by']:
            raise serializer.ValidationError('Ride offered on behalf of others are not allowed')
        user = data['offered_by']
        circle = self.context['circle']
      
        try:
            membership=MemberShip.objects.get(
                user=user,
                circle=circle,
                is_active=True)
        except MemberShip.DoesNotExist:
            raise serializers.ValidationError('user is not an active member of circle')

        # La llegada tiene que ser despues de la salida, si la salida es mayor o igual a la llegada marca error
        if data['arrival_date']<=data['departure_date']:
            raise serializers.ValidationError('Departure date must happen offer arrival date')
            
        self.context['membership']=membership
        return data


    def create(self,data):
        """ Create ride and update stats """
        circle = self.context['circle']
        ride = Rides.objects.create(**data,offered_in=circle)

        #update informacion del Circle
        circle.rides_offered+=1
        circle.save()

        # Membership update 
        membership=self.context['membership'] 
        membership.rides_offered+=1
        membership.save()

        #profile
        profile = data['offered_by'].profile #es un objeto de tipo user
        profile.rides_offered+=1
        profile.save()

        return ride 



class JoinRideSerializer(serializers.ModelSerializer):
    """ Join Ride serializer """

    passanger= serializers.IntegerField()

    class Meta:
        model= Rides
        fields=('passanger',)

    def validate_passanger(self,data):
        """ Verify passenger exist and is a circle member """
        try:
            user=User.objects.get(pk=data) 
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid Passanger')


        circle= self.context['circle']
        try:
            membership=MemberShip.objects.get(
                user=user,circle=circle,is_active=True
                )
        except MemberShip.DoesNotExist:
            raise serializers.ValidationError('no es miembro')

        self.context['member']=membership
        self.context['user']=user
        return data

    # verificamos que el ride no esta vacio
    def validate(self,data):
        """ verify ride allow new passangers """
        offset= timezone.now()- timedelta(minutes=10)
        ride = self.context['ride']
        if ride.departure_date<= offset:
            raise serializers.ValidationError("You cant join this ride now")

        if ride.avaible_seats< 1:
            raise serializers.ValidationError('Ride is alredy full')
    
        if ride.passangers.filter(pk=self.context['user'].pk).exists():
            raise serializers.ValidationError('Passenger is already in this trip')
        import pdb;pdb.set_trace()
        return data

    def update(self,instance,data):
        """ Add passenger to ride, and update stats """
        ride = self.context['ride']
        circle= self.context ['circle']
        user = self.context['user']
           
        ride.passangers.add(user)
        # Profile 
        profile = user.profile 
        profile.rides_taken += 1
        profile.save()

        #Membership
        member = self.context['member']
        member.rides_taken +=1
        member.save()

        #Circle
        circle = self.context['circle']
        circle.rides_taken +=1
        circle.save()

        return ride 


class EndRideSerializer(serializers.ModelSerializer):
    """ End ride serializer """

    current_time = serializers.DateTimeField()
    class Meta:
        model= Rides
        fields=('is_active','current_time')

        
    def validate_current_time(self,data):
        """ verify ride have indeed started """
        # cuando la fecha actual esta adelnta de la fecha de inicio eso significa que el viaje ya inicio
        # si ya inicio todo esta bien 
        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.ValidationError('Ride has not started yet')

        return data 



class SocoreRideSerializer(serializers.ModelSerializer):
    """ Score Ride serializer """
    passanger = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score =serializers.IntegerField(min_value=0,max_value=15)

    
    class Meta:
        model=Raitings
        fields=(
            'passanger',
            'score'
        )
    
    def validate(self,data):
        """ Verify qeu el usuario pertenece al ride y el ride esta finalizado"""
        ride= self.context['view'].get_object()
        user = data['passanger']

       
        if not ride.passangers.filter(pk=user.pk).exists():
            raise serializers.ValidationError('El pasajero no esta en este ride')

        if Raitings.objects.filter(ride=ride,passanger=user).exists():
            raise serializers.ValidationError('El pasajero ya dio su puntuacion')


       # si el ride esta activo     
        if ride.is_active:
            raise serializers.ValidationError('El ride aún no esta finalizado') 
        

        return data

    def create(self,data):
        """ Create new circle member """
        # Se sobre escribe el metodo create porque se tiene que agregar el invited_by y updatear en la tabla membership
        
        ride = self.context['view'].get_object()
        score_num = self.data['score']
        score = Raitings.objects.create(
            passanger = data['passanger'],
            ride=ride,
            score=score_num
        )

        raiting_avg=Raitings.objects.filter(ride=ride).aggregate(Avg('score'))
        # update
        ride.rating=raiting_avg['score__avg']
        ride.save()
        
        
        return score 

        

        
        

    
