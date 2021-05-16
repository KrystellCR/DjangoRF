""" Circle serializers """
from rest_framework import serializers

#Model
from circles.models import Circle

class CircleModelSerializer(serializers.ModelSerializer):
    
    """ Se valida de forma diferente a com oesta registrado en el modelo"""
    members_limit = serializers.IntegerField(
        required=False,
        min_value=10,
        max_value=1243,

    )
    is_limited= serializers.BooleanField(default=False)

    class Meta:
        model=Circle
        # Estos campos se validarán a como estan registrados en el modelo
        fields=('id','name','slug_name','about',
        'rides_offered','rides_taken','verified','is_public',
        'is_limited','members_limit')

        read_only_fields=(
            'is_public',
            'verified',
            'rides_offered',
            'rides_taken'
        )
    def validate(self,data):
        """ Ensure both memebers_limit and is_limited are present """
        # Toma los datos del data y si no se mandaron los setea en None o false respectivamente 
        members_limit= data.get('members_limit',None)
        is_limited = data.get('is_limited',False)


        # Si existe alguna de las dos tiene que estar la otra 
        if bool(members_limit) ^ is_limited: #XOR
              raise serializers.ValidationError('If cirlce is limit a memeber limited must be provide .')

        return data


