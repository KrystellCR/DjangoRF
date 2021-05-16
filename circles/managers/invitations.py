""" Circle invitation managers """

# django
from django.db import models

#Utilities
import random
from string import ascii_uppercase,digits


class InvitationManager(models.Manager):
    """ Invitation manager 
    Used to handle code creation 
    """
    CODE_LENGTH= 10
    def create(self,**kwargs):
        """ Handel code creation """
        pool = ascii_uppercase + digits +'.-'
        #code =kwargs.get('code',''.join(random.choices(pool,k=self.CODE_LENGTH)))
        code =kwargs.get('code',''.join(random.choice(pool)))
        # si recibe un code checo si existe y si existe genero uno de manera aleatoria
        while self.filter(code=code).exists():
            code = ''.join(random.choices(random.choice(pool)))
        
        kwargs['code']=code
        return super(InvitationManager,self).create(**kwargs)
