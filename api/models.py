
from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL



class Profile(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    img_url = models.TextField(null=True, blank=True)

class Wallet(models.Model):
    address = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=SET_NULL)
    last_authenticated = models.DateTimeField(null=True, blank=True)

class Contract(models.Model):
    address = models.CharField(max_length=100, unique=True)

class Token(models.Model):
    contract = models.ForeignKey(Contract, on_delete=CASCADE)
    token_identifier = models.CharField(max_length=500)
    creator = models.ForeignKey(Wallet, null=True, blank=True, on_delete=SET_NULL)

class LikeHistory(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    token = models.ForeignKey(Token, on_delete=CASCADE)
    profile = models.ForeignKey(Profile, on_delete=CASCADE)
    value = models.IntegerField() # +1 or -1 for like/unlike
