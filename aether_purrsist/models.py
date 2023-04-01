from tortoise.models import Model
from tortoise import fields


class Threads(Model):
    Fingerprint = fields.CharField(pk=True, max_length=64)
    Board = fields.CharField(max_length=64)

    Name = fields.CharField(max_length=255)
    Body = fields.TextField()
    Link = fields.CharField(max_length=5000)
    Owner = fields.CharField(max_length=64)
    OwnerPublicKey = fields.CharField(max_length=64)

    LocalArrival = fields.DatetimeField(auto_now=False)
    LastReferenced = fields.DatetimeField(auto_now=False)


class PublicKeys(Model):
    Fingerprint = fields.CharField(pk=True, max_length=64)

    Name = fields.CharField(max_length=64)
    Type = fields.CharField(max_length=64)
    PublicKey = fields.TextField()


class Boards(Model):
    Fingerprint = fields.CharField(pk=True, max_length=64)
    Name = fields.CharField(max_length=255)
    Owner = fields.CharField(max_length=64)
    OwnerPublicKey = fields.CharField(max_length=64)
    Description = fields.TextField()
    Creation = fields.IntField()
    Language = fields.CharField(max_length=3)

    LocalArrival = fields.DatetimeField(auto_now=False)


class Posts(Model):
    Fingerprint = fields.CharField(pk=True, max_length=64)
    Board = fields.CharField(max_length=64)
    Thread = fields.CharField(max_length=64)  # thread it belongs to
    Parent = fields.CharField(max_length=64)  # parent post

    Body = fields.TextField()
    Owner = fields.CharField(max_length=64)
    Creation = fields.IntField()
    LastUpdate = fields.IntField()

    LocalArrival = fields.DatetimeField(auto_now=False)
    LastReferenced = fields.DatetimeField(auto_now=False)