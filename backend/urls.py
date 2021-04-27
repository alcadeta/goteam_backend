from django.urls import path
from main.api.api_auth import register, login, verify_token
from main.api.api_users import users
from main.api.api_teams import teams
from main.api.api_boards import boards
from main.api.api_columns import columns
from main.api.api_tasks import tasks
from main.api.api_subtasks import subtasks

urlpatterns = [
    path('verify-token/', verify_token, name='verifytoken'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/', users, name='users'),
    path('teams/', teams, name='teams'),
    path('boards/', boards, name='boards'),
    path('columns/', columns, name='columns'),
    path('tasks/', tasks, name='tasks'),
    path('subtasks/', subtasks, name='subtasks'),
]
