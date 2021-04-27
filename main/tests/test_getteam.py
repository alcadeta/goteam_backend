from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Team
from ..util import create_admin, create_member
from ..validation.val_auth import \
    not_authenticated_response, not_authorized_response


class GetTeamTests(APITestCase):
    endpoint = '/teams/?team_id='

    def setUp(self):
        self.team = Team.objects.create()
        self.admin = create_admin(self.team)
        self.member = create_member(self.team)
        self.wrong_admin = create_admin(Team.objects.create(), '1')

    def test_success(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'id': self.team.id,
            'inviteCode': self.team.invite_code
        })

    def test_team_id_empty(self):
        response = self.client.get(self.endpoint,
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team ID cannot be empty.',
                                   code='blank')
        })

    def test_team_id_invalid(self):
        response = self.client.get(f'{self.endpoint}asdfsa',
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team ID must be a number.',
                                   code='invalid')
        })

    def test_team_not_found(self):
        response = self.client.get(f'{self.endpoint}12314241',
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team not found.',
                                   code='not_found')
        })

    def test_auth_user_empty(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER='',
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_user_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER='invalidusername',
                                   HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_empty(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER=self.admin['username'],
                                   HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfosia')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_wrong_team(self):
        response = self.client.get(
            f'{self.endpoint}{self.team.id}',
            HTTP_AUTH_USER=self.wrong_admin['username'],
            HTTP_AUTH_TOKEN=self.wrong_admin['token']
        )
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_unauthorized(self):
        response = self.client.get(f'{self.endpoint}{self.team.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authorized_response.data)
