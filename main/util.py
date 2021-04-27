from main.models import User
from rest_framework.response import Response
from .serializers.ser_board import BoardSerializer
from .serializers.ser_column import ColumnSerializer
import bcrypt


def create_admin(team, username_suffix=''):
    user = User.objects.create(
        username=f'teamadmin{username_suffix}',
        password=b'$2b$12$DKVJHUAQNZqIvoi.OMN6v.x1ZhscKhbzSxpOBMykHgTIMeeJpC6m'
                 b'e',
        is_admin=True,
        team=team
    )
    token = '$2b$12$yGUdlz0eMW3P6TAX07.CPuCA5u.t10uTEKCE2SQ5Vdm3VbnrHbpoK'
    return {'username': user.username,
            'password': user.password,
            'password_raw': 'barbarbar',
            'is_admin': user.is_admin,
            'team': user.team,
            'token': token if not username_suffix else bcrypt.hashpw(
                bytes(user.username, 'utf-8') + user.password,
                bcrypt.gensalt()
            ).decode('utf-8')}


def create_member(team, username_suffix=''):
    user = User.objects.create(
        username=f'teammember{username_suffix}',
        password=b'$2b$12$DKVJHUAQNZqIvoi.OMN6v.x1ZhscKhbzSxpOBMykHgTIMeeJpC6m'
                 b'e',
        is_admin=False,
        team=team
    )
    token = '$2b$12$qNhh2i1ZPU1qaIKncI7J6O2kr4XmuCWSwLEMJF653vyvDMIRekzLO'
    return {'username': user.username,
            'password': user.password,
            'password_raw': 'barbarbar',
            'is_admin': user.is_admin,
            'team': user.team,
            'token': token if not username_suffix else bcrypt.hashpw(
                bytes(user.username, 'utf-8') + user.password,
                bcrypt.gensalt()
            ).decode('utf-8')}

def create_board(team_id, name):  # -> (board, response)
    board_serializer = BoardSerializer(data={'team': team_id, 'name': name})
    if not board_serializer.is_valid():
        return None, Response(board_serializer.errors, 400)

    board = board_serializer.save()

    team_admin = User.objects.get(team_id=team_id, is_admin=True)

    board.user.add(team_admin)

    # create four columns for the board
    for order in range(0, 4):
        column_serializer = ColumnSerializer(
            data={'board': board.id, 'order': order}
        )
        if not column_serializer.is_valid():
            return board, Response(
                column_serializer.errors, 400
            )
        column_serializer.save()

    return board, None

