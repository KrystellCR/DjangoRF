from django.contrib import admin

# Register your models here.
from .models import Circle,MemberShip

# Register your models here.
@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
	
	#para que aparezcan los atributos de profile en la lista 
	list_display = ('pk','name','slug_name','about','rides_offered','rides_taken','verified','is_public','is_limited','members_limit') 


@admin.register(MemberShip)
class MemberShipAdmin(admin.ModelAdmin):
	
	#para que aparezcan los atributos de profile en la lista 
	list_display = ('pk','user','profile','circle','is_admin','is_active','used_invitations','remaining_invitations','invited_by') 