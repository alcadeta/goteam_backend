from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Board, Team, Column
from ..util import create_member, create_admin
from ..validation.val_auth import \
    not_authenticated_response, not_authorized_response


class PostBoardTests(APITestCase):
    endpoint = '/boards/'

    def setUp(self):
        self.team = Team.objects.create()
        self.member = create_member(self.team)
        self.admin = create_admin(self.team)
        self.wrong_admin = create_admin(Team.objects.create(), '1')

    def test_success(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER=self.admin['username'],
            HTTP_AUTH_TOKEN=self.admin['token']
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('msg'),
                         'Board creation successful.')
        board = Board.objects.get(id=response.data.get('id'))
        columns = Column.objects.filter(board=board.id)
        self.assertEqual(len(columns), 4)
        self.assertEqual(Board.objects.count(), initial_count + 1)

    def test_board_name_empty(self):
        initial_boards_count = Board.objects.count()
        initial_columns_count = Column.objects.count()
        response = self.client.post(self.endpoint,
                                    {'team_id': self.team.id, 'name': ''},
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'name': [ErrorDetail(string='Board name cannot be empty.',
                                 code='blank')]
        })
        self.assertEqual(Board.objects.count(), initial_boards_count)
        self.assertEqual(Column.objects.count(), initial_columns_count)

    def test_unauthorized(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER=self.member['username'],
            HTTP_AUTH_TOKEN=self.member['token']
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authorized_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_team_id_blank(self):
        initial_count = Board.objects.count()
        response = self.client.post(self.endpoint,
                                    {'team_id': '', 'name': 'New Board'},
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team ID cannot be empty.',
                                   code='blank')
        })
        self.assertEqual(Board.objects.count(), initial_count)

    def test_team_not_found(self):
        initial_count = Board.objects.count()
        response = self.client.post(self.endpoint,
                                    {'team_id': 124123, 'name': 'New Board'},
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'team_id': ErrorDetail(string='Team not found.', code='not_found')
        })
        self.assertEqual(Board.objects.count(), initial_count)

    def test_auth_token_empty(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER=self.admin['username'],
            HTTP_AUTH_TOKEN=''
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_auth_token_invalid(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER=self.admin['username'],
            HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfosi'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_auth_user_blank(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER='',
            HTTP_AUTH_TOKEN=self.admin['token']
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_auth_user_invalid(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER='invalidio',
            HTTP_AUTH_TOKEN=self.admin['token']
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_wrong_team(self):
        initial_count = Board.objects.count()
        response = self.client.post(
            self.endpoint,
            {'team_id': self.team.id, 'name': 'New Board'},
            HTTP_AUTH_USER=self.wrong_admin['username'],
            HTTP_AUTH_TOKEN=self.wrong_admin['token']
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)
