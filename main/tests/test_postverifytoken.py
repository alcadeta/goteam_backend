from rest_framework.test import APITestCase
from main.models import Team
from ..util import create_member


class VerifyTokenTests(APITestCase):
    endpoint = '/verify-token/'

    def setUp(self):
        self.user = create_member(Team.objects.create())

    def test_success(self):
        request_data = {'username': self.user['username'],
                        'token': self.user['token']}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'msg': 'Token verification success.',
            'username': self.user['username'],
            'teamId': self.user['team'].id,
            'isAdmin': self.user['is_admin']
        })

    def test_token_invalid(self):
        request_data = {'username': self.user['username'],
                        'token': 'as/dlkfjAS:DFkjaSdlnflasdjnvkasdjfasd,fasbd'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'msg': 'Token verification failure.'})

    def test_token_empty(self):
        request_data = {'username': self.user['username'],
                        'token': ''}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'msg': 'Token verification failure.'})

    def test_username_invalid(self):
        request_data = {'username': 'nonexistent',
                        'token': 'as/dlkfjAS:DFkjaSdlnflasdjnvkasdjfasd,fasbd'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'msg': 'Token verification failure.'})

    def test_username_empty(self):
        request_data = {'username': '',
                        'token': 'as/dlkfjAS:DFkjaSdlnflasdjnvkasdjfasd,fasbd'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'msg': 'Token verification failure.'})
