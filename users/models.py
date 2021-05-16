from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	"""
	picture= models.ImageField(
		'profile picture',
		upload_to='users/pictures',
		blank=True, # puede ser nulo o blanco 
		null=True
	) # Instalamos pillow  """
	
	phone_number = models.CharField(max_length=20,blank=True)
	is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='set true cuando el usuario es verificiado con su email')	
	#para regresar un string en lugar de un object con id cuando estamso en la cosola	
	
	biography= models.TextField(max_length=500,blank=True)

	#Stats
	rides_taken= models.PositiveIntegerField(default=0)
	rides_offered= models.PositiveIntegerField(default=0)
	reputation= models.FloatField(
		default=5.0,
		help_text="user's reputation based on the rides taken offerd"
	)



	def __str__(self):
		"""return a string username """
		#user porque username esta en user no en profile y estamos usando un proxy
		return self.user.username