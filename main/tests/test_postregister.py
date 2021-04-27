from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from main.models import User, Team, Board
from uuid import uuid4


class RegisterTests(APITestCase):
    endpoint = '/register/'

    def setUp(self):
        self.team = Team.objects.create()
        Board.objects.create(team=self.team)

    def help_test_success(self,
                          initial_user_count,
                          request_data,
                          url_suffix=''):
        response = self.client.post(f'{self.endpoint}{url_suffix}',
                                    request_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('msg'), 'Registration successful.')
        self.assertEqual(response.data.get('username'),
                         request_data['username'])
        self.assertTrue(response.data.get('token'))
        user = User.objects.get(username=response.data['username'])
        self.assertTrue(user)
        team = Team.objects.get(user=user)
        self.assertTrue(team)
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        return user

    def test_success(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        initial_board_count = Board.objects.count()
        self.help_test_success(initial_user_count, {
            'username': 'fooooooooo',
            'password': 'barbarbar',
            'password_confirmation': 'barbarbar'
        })
        self.assertEqual(Team.objects.count(), initial_team_count + 1)
        self.assertEqual(Board.objects.count(), initial_board_count)

    def test_success_with_invite_code(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        user = self.help_test_success(initial_user_count, {
            'username': 'foooo',
            'password': 'barbarbar',
            'password_confirmation': 'barbarbar',
        }, f'?invite_code={self.team.invite_code}')
        self.assertEqual(Team.objects.count(), initial_team_count)
        self.assertEqual(user.team, self.team)

    def test_username_max_length(self):
        initial_user_count = User.objects.count()
        request_data = {'username': 'fooooooooooooooooooooooooooooooooooo',
                        'password': 'barbarbar',
                        'password_confirmation': 'barbarbar'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': [ErrorDetail(
                string='Username cannot be longer than 35 characters.',
                code='max_length'
            )]
        })
        self.assertEqual(User.objects.count(), initial_user_count)

    # noinspection DuplicatedCode
    def test_password_max_length(self):
        password = '''
            barbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarb
            arbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarba
            rbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbar
            barbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarba
        '''
        request_data = {'username': 'foooo',
                        'password': password}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password': [ErrorDetail(
                string='Password cannot be longer than 255 characters.',
                code='max_length'
            )]
        })

    def test_invalid_invite_code(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        request_data = {'username': 'foooo',
                        'password': 'barbarbar',
                        'password_confirmation': 'barbarbar',
                        'invite_code': 'invalid uuid'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'invite_code': [ErrorDetail(string='Invalid invite code.',
                                        code='invalid')]
        })
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Team.objects.count(), initial_team_count)

    def test_team_not_found(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        request_data = {'username': 'foooo',
                        'password': 'barbarbar',
                        'password_confirmation': 'barbarbar',
                        'invite_code': uuid4()}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'invite_code': [ErrorDetail(string='Team not found.',
                                        code='invalid')]
        })
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Team.objects.count(), initial_team_count)

    def test_unmatched_passwords(self):
        initial_count = User.objects.count()
        response = self.client.post(self.endpoint, {
            'username': 'foooo',
            'password_confirmation': 'barbarbar',
            'password': 'not_barbarbar'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password_confirmation': ErrorDetail(
                string='Confirmation must match the password.',
                code='no_match'
            )
        })

        self.assertEqual(User.objects.count(), initial_count)

    def test_username_blank(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        request_data = {'username': '',
                        'password': 'barbarbar',
                        'password_confirmation': 'barbarbar'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': [ErrorDetail(string='Username cannot be empty.',
                                     code='blank')]
        })
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Team.objects.count(), initial_team_count)

    def test_password_blank(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        request_data = {'username': 'foooo',
                        'password': '',
                        'password_confirmation': 'barbarbar'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password': [ErrorDetail(string='Password cannot be empty.',
                                     code='blank')]
        })
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Team.objects.count(), initial_team_count)

    def test_password_confirmation_blank(self):
        initial_user_count = User.objects.count()
        initial_team_count = Team.objects.count()
        request_data = {'username': 'foooo',
                        'password': 'barbarbar',
                        'password_confirmation': ''}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password_confirmation': ErrorDetail(
                string='Password confirmation cannot be empty.',
                code='blank'
            )
        })
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Team.objects.count(), initial_team_count)
