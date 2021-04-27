from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Team, User, Board
from ..validation.val_auth import not_authenticated_response
from ..util import create_member


class GetUsersTests(APITestCase):
    def setUp(self):
        self.team = Team.objects.create()
        self.users = [
            User.objects.create(
                username=f'User #{i}',
                password=b'$2b$12$DKVJHUAQNZqIvoi.OMN6v.x1ZhscKhbzSxpOBMykHgTI'
                         b'MeeJpC6m',
                is_admin=False,
                team=self.team
            ) for i in range(0, 3)
        ]
        self.username = self.users[0].username
        self.token = '$2b$12$WLmxQnf9kbDoW/8jA6kfIO9TfchCiGphBpckS2oy755wtdT' \
                     'aIQsoq'
        self.board = Board.objects.create(name='Board', team=self.team)
        self.board.user.add(self.users[0])
        self.wrong_member = create_member(Team.objects.create(), '1')

    def get_users(self, team_id, board_id, auth_user, auth_token):
        return self.client.get(
            f'/users/?team_id={team_id}&board_id={board_id}',
            HTTP_AUTH_USER=auth_user,
            HTTP_AUTH_TOKEN=auth_token
        )

    def test_success(self):
        response = self.get_users(self.team.id,
                                  self.board.id,
                                  self.username,
                                  self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, list(map(
            lambda i_user: {'username': i_user[1].username,
                            'isActive': i_user[0] == 0,
                            'isAdmin': i_user[1].is_admin},
            enumerate(self.users)
        )))

    def test_team_id_blank(self):
        response = self.get_users('', self.board.id, self.username, self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team ID cannot be empty.',
                                   code='blank')
        })

    def test_team_id_invalid(self):
        response = self.get_users('qwert',
                                  self.board.id,
                                  self.username,
                                  self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team ID must be a number.',
                                   code='invalid')
        })

    def test_team_not_found(self):
        response = self.get_users('12412312',
                                  self.board.id,
                                  self.username,
                                  self.token)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team not found.',
                                   code='not_found')
        })

    def test_board_id_blank(self):
        response = self.get_users(self.team.id, '', self.username, self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID cannot be empty.',
                                    code='blank')
        })

    def test_board_id_invalid(self):
        response = self.get_users(self.team.id,
                                  'asldfjasldjf',
                                  self.username,
                                  self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID must be a number.',
                                    code='invalid')
        })

    def test_board_not_found(self):
        response = self.get_users(self.team.id,
                                  '123891231',
                                  self.username,
                                  self.token)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board not found.',
                                    code='not_found')
        })

    def test_auth_user_invalid(self):
        response = self.get_users('12412312', self.board.id, 'foo', self.token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_empty(self):
        response = self.get_users(self.team.id,
                                  self.board.id,
                                  self.username,
                                  '')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_wrong_team(self):
        response = self.get_users(self.team.id,
                                  self.board.id,
                                  self.wrong_member['username'],
                                  self.wrong_member['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_invalid(self):
        response = self.get_users(self.team.id,
                                  self.board.id,
                                  self.username,
                                  'AFW£IJA')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

