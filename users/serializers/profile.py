""" Profile serializer """

# Django RF
from rest_framework import serializers
#Models
from users.models import Profile

class ProfileModelSerializer(serializers.ModelSerializer):
    """ Profile Model Serializer"""
    class Meta:
        model = Profile
        fields=(
            #'picture',
            'biography',
            'rides_taken',
            'rides_offered',
            'reputation'
            
        )
        read_only_fields=(
            'rides_taken',
            'rides_offered',
            'reputation'
        )