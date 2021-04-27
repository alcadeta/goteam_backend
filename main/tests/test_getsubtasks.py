from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Subtask, Task, Column, Board, Team
from ..util import create_member
from ..validation.val_auth import not_authenticated_response


class GetSubtasksTests(APITestCase):
    endpoint = '/subtasks/?task_id='

    def setUp(self):
        team = Team.objects.create()
        board = Board.objects.create(team=team)
        self.column = Column.objects.create(order=0, board=board)
        self.task = Task.objects.create(title='Some Task',
                                        order=0,
                                        column=self.column)
        subtasks_raw = [
            Subtask.objects.create(
                title=f'Subtask #{i}',
                order=i,
                done=True if i == 1 else False,
                task=self.task
            ) for i in range(0, 3)
        ]
        self.subtasks = list(
            map(
                lambda subtask: {'id': subtask.id,
                                 'order': subtask.order,
                                 'title': subtask.title,
                                 'done': subtask.done}
                , subtasks_raw
            )
        )
        self.member = create_member(team)
        self.wrong_member = create_member(Team.objects.create(), '4')

    def test_success(self):
        response = self.client.get(f'{self.endpoint}{self.task.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('subtasks'), self.subtasks)

    def test_task_id_empty(self):
        response = self.client.get(self.endpoint,
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'task_id': ErrorDetail(string='Task ID cannot be empty.',
                                   code='blank')
        })

    def test_task_id_invalid(self):
        response = self.client.get(f'{self.endpoint}aksjda',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'task_id': ErrorDetail(string='Task ID must be a number.',
                                   code='invalid')
        })

    def test_task_not_found(self):
        response = self.client.get(f'{self.endpoint}1231231',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'task_id': ErrorDetail(string='Task not found.',
                                   code='not_found')
        })

    def test_auth_user_empty(self):
        response = self.client.get(f'{self.endpoint}{self.task.id}',
                                   HTTP_AUTH_USER='',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_user_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.task.id}',
                                   HTTP_AUTH_USER='invalidusername',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_empty(self):
        response = self.client.get(f'{self.endpoint}{self.task.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.task.id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfosia')
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_wrong_team(self):
        response = self.client.get(
            f'{self.endpoint}{self.task.id}',
            HTTP_AUTH_USER=self.wrong_member['username'],
            HTTP_AUTH_TOKEN=self.wrong_member['token']
        )
        self.assertEqual(response.status_code,
                         not_authenticated_response.status_code)
        self.assertEqual(response.data, not_authenticated_response.data)
