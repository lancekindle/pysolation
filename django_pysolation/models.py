from django.db import models

class Board(models.Model):
    pk_id = models.AutoField(primary_key=True)
    w = models.IntegerField()
    h = models.IntegerField()

class Tile(models.Model):
    pk_id = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    ID = models.CharField(max_length=15)
    visible = models.BooleanField()
    solid = models.BooleanField()

class Player(models.Model):
    pk_id = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    ID = models.CharField(max_length=15)  # player_1, player_2, etc.
    x = models.IntegerField()
    y = models.IntegerField()
    disabled = models.BooleanField()    # True if player is unable to move
    active = models.BooleanField()  # True if it's players turn
