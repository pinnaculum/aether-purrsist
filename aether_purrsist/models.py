from tortoise.models import Model
from tortoise import fields


class Base(Model):
    """
    Common SQL fields in the Aether database
    """

    EncrContent = fields.TextField()
    Fingerprint = fields.CharField(pk=True, max_length=64)

    LocalArrival = fields.DatetimeField(auto_now=False)
    LastReferenced = fields.DatetimeField(auto_now=False)

    Owner = fields.CharField(max_length=64)
    OwnerPublicKey = fields.CharField(max_length=64)

    Meta = fields.TextField()
    RealmId = fields.CharField(max_length=64)


class Threads(Base):
    Board = fields.CharField(max_length=64)
    Body = fields.TextField()
    Link = fields.CharField(max_length=5000)
    Name = fields.CharField(max_length=255)


class PublicKeys(Model):
    Fingerprint = fields.CharField(pk=True, max_length=64)

    Name = fields.CharField(max_length=64)
    Type = fields.CharField(max_length=64)
    PublicKey = fields.TextField()


class Boards(Base):
    Name = fields.CharField(max_length=255)
    Description = fields.TextField()
    Creation = fields.IntField()
    Language = fields.CharField(max_length=3)


class Posts(Base):
    Board = fields.CharField(max_length=64)
    Thread = fields.CharField(max_length=64)  # thread it belongs to
    Parent = fields.CharField(max_length=64)  # parent post

    Body = fields.TextField()
    Creation = fields.IntField()
    LastUpdate = fields.IntField()


class Votes(Base):
    Board = fields.CharField(max_length=64)
    Thread = fields.CharField(max_length=64)
    Target = fields.CharField(max_length=64)  # object voted on ?

    Type = fields.IntField()
    TypeClass = fields.IntField()
