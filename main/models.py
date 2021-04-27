from django.db.models import *
import uuid


class Team(Model):
    invite_code = UUIDField(default=uuid.uuid4)


class User(Model):
    username = CharField(primary_key=True, max_length=35)
    password = BinaryField()
    is_admin = BooleanField(default=False)
    team = ForeignKey(Team, on_delete=CASCADE)


class Board(Model):
    name = CharField(max_length=35)
    team = ForeignKey(Team, on_delete=CASCADE)
    user = ManyToManyField(User)


class Column(Model):
    order = IntegerField()
    board = ForeignKey(Board, on_delete=CASCADE)


class Task(Model):
    title = CharField(max_length=50)
    description = TextField(blank=True, null=True)
    order = IntegerField()
    column = ForeignKey(Column, on_delete=CASCADE)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)


class Subtask(Model):
    title = CharField(max_length=50)
    order = IntegerField()
    task = ForeignKey(Task, on_delete=CASCADE)
    done = BooleanField(default=False)
