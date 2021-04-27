from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Team, User
from ..util import create_admin, create_member
from ..validation.val_auth import \
    not_authenticated_response, not_authorized_response


class DeleteUserTests(APITestCase):
    def setUp(self):
        self.team = Team.objects.create()
        self.admin = create_admin(self.team)
        self.member = create_member(self.team)
        self.wrong_admin = create_admin(Team.objects.create(), '1')

    def delete_user(self, username, auth_user, auth_token):
        return self.client.delete(f'/users/?username={username}',
                                  HTTP_AUTH_USER=auth_user,
                                  HTTP_AUTH_TOKEN=auth_token)

    def test_success(self):
        response = self.delete_user(self.member['username'],
                                    self.admin['username'],
                                    self.admin['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'msg': 'Member has been deleted successfully.',
        })
        self.assertFalse(User.objects.filter(username=self.member['username']))

    def test_cant_delete_admin(self):
        response = self.delete_user(self.admin['username'],
                                    self.admin['username'],
                                    self.admin['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {
            'username': ErrorDetail(
                string='Team leaders cannot be deleted from their teams.',
                code='forbidden'
            )
        })
        self.assertTrue(User.objects.filter(username=self.admin['username']))

    def test_username_blank(self):
        response = self.delete_user('',
                                    self.admin['username'],
                                    self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': ErrorDetail(string='Username cannot be empty.',
                                    code='blank')
        })
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_user_not_found(self):
        response = self.delete_user('piquelitta',
                                    self.admin['username'],
                                    self.admin['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'username': ErrorDetail(string='User not found.',
                                    code='not_found')
        })
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_auth_token_empty(self):
        response = self.delete_user(self.member['username'],
                                    self.admin['username'],
                                    '')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_auth_token_invalid(self):
        response = self.delete_user(self.member['username'],
                                    self.admin['username'],
                                    'kasjdaksdjalsdkjasd')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_auth_user_blank(self):
        response = self.delete_user(self.member['username'],
                                    '',
                                    self.admin['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_auth_user_invalid(self):
        response = self.delete_user(self.member['username'],
                                    'invaliditto',
                                    self.admin['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_wrong_team(self):
        response = self.delete_user(self.member['username'],
                                    self.wrong_admin['username'],
                                    self.wrong_admin['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authorized_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

    def test_unauthorized(self):
        response = self.delete_user(self.member['username'],
                                    self.member['username'],
                                    self.member['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authorized_response.data)
        self.assertTrue(User.objects.filter(username=self.member['username']))

