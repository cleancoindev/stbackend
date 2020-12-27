
from django.db import models
from django.db.models.deletion import CASCADE

class MagicUser(models.Model):
    email = models.CharField(max_length=255, unique=True)

class Contract(models.Model):
    address = models.CharField(max_length=100, unique=True)

class Token(models.Model):
    contract = models.ForeignKey(Contract, on_delete=CASCADE)
    token_identifier = models.CharField(max_length=500)

class LikeHistory(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    token = models.ForeignKey(Token, on_delete=CASCADE)
    magic_user = models.ForeignKey(MagicUser, on_delete=CASCADE)
    value = models.IntegerField() # +1 or -1 for like/unlike
