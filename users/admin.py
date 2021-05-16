from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	
	#para que aparezcan los atributos de profile en la lista 
	list_display = ('pk','user','phone_number','is_verified') 