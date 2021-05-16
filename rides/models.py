from django.db import models
from django.contrib.auth.models import User
from circles.models import Circle,MemberShip


# Create your models here.
class Rides(models.Model):
    
    offered_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    offered_in= models.ForeignKey(Circle,on_delete=models.SET_NULL,null=True)

    passangers=models.ManyToManyField(User,related_name='passangers')
    #asientes disponibles
    avaible_seats=models.PositiveSmallIntegerField(default=1)
    comments=models.TextField(blank=True)

    # calle o colonia 
    departure_location=models.CharField(max_length=255)
    departure_date=models.DateTimeField()
    arrival_location=models.CharField(max_length=255)
    arrival_date=models.DateTimeField()

    rating=models.FloatField(null=True)

    is_active=models.BooleanField(
        'active status',
        default=True,
        help_text='Used for disabling the ride or makingit as fimnished'
    )

    def __str__(self):
        """Return ride details."""
        return '{_from} to {to} | {day} {i_time} - {f_time}'.format(
            _from=self.departure_location,
            to=self.arrival_location,
            day=self.departure_date.strftime('%a %d, %b'),
            i_time=self.departure_date.strftime('%I:%M %p'),
            f_time=self.arrival_date.strftime('%I:%M %p'),
        )



class Raitings(models.Model):
    passanger = models.ForeignKey(
        User,
        null=True,
        on_delete = models.SET_NULL
    )
    ride = models.ForeignKey(
        Rides,
        null=True,# porque puede ser que nadie te invito y tu creste el grupo
        on_delete = models.CASCADE, # para que se borre cuando se borre el ride 
        related_name='invited_by'
    )
    score=models.PositiveSmallIntegerField(default=1)