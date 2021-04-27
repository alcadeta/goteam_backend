from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Task, Column, Board, Team
from ..util import create_member
from ..validation.val_auth import not_authenticated_response


class GetTasksTests(APITestCase):
    endpoint = '/tasks/?column_id='

    def setUp(self):
        team = Team.objects.create()
        board = Board.objects.create(team=team)
        self.column = Column.objects.create(order=0, board=board)
        tasks_raw = [
            Task.objects.create(
                title=f'Task #{i}',
                order=i,
                column=self.column
            ) for i in range(0, 10)
        ]
        self.tasks = list(
            map(
                lambda task: {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'order': task.order
                }, tasks_raw
            )
        )
        self.member = create_member(team)
        self.wrong_member = create_member(Team.objects.create(), '1')

    def test_success(self):
        response = self.client.get(f'{self.endpoint}{self.column.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        print(f'§response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('tasks'), self.tasks)

    def test_column_id_empty(self):
        response = self.client.get(self.endpoint,
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'column_id': ErrorDetail(string='Column ID cannot be empty.',
                                     code='blank')
        })

    def test_column_id_invalid(self):
        response = self.client.get(f'{self.endpoint}aksjda',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'column_id': ErrorDetail(string='Column ID must be a number.',
                                     code='invalid')
        })

    def test_column_not_found(self):
        response = self.client.get(f'{self.endpoint}1231231',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'column_id': ErrorDetail(string='Column not found.',
                                     code='not_found')
        })

    def test_auth_user_empty(self):
        response = self.client.get(f'{self.endpoint}{self.column.id}',
                                   HTTP_AUTH_USER='',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_user_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.column.id}',
                                   HTTP_AUTH_USER='invalidusername',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_empty(self):
        response = self.client.get(f'{self.endpoint}{self.column.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.column.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfosia')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_wrong_team(self):
        response = self.client.get(
            f'{self.endpoint}{self.column.id}',
            HTTP_AUTH_USER=self.wrong_member['username'],
            HTTP_AUTH_TOKEN=self.wrong_member['token']
        )
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)
