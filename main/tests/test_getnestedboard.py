from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Board, Team, Column, Task, Subtask, User
from ..util import create_member
from ..validation.val_auth import \
    not_authenticated_response, not_authorized_response


class GetNestedBoardTests(APITestCase):
    endpoint = '/boards/?id='

    def setUp(self):
        self.team = Team.objects.create()
        self.member = create_member(self.team)
        self.wrong_team_member = create_member(Team.objects.create(), '1')
        self.wrong_board_member = create_member(self.team, '2')
        self.boards = []
        member = User.objects.get(username=self.member['username'])
        wrong_team_member = User.objects.get(
            username=self.wrong_team_member['username']
        )
        for _ in range(0, 3):
            board = Board.objects.create(team_id=self.team.id)
            board.user.add(member)
            board.user.add(wrong_team_member)
            self.boards.append(board)
        self.columns = [
            Column.objects.create(
                board_id=self.boards[0].id, order=i
            ) for i in range(0, 4)
        ]
        self.tasks = [
            Task.objects.create(
                title=f'Task #{i}',
                order=i,
                column=self.columns[0],
                user=member
            ) for i in range(0, 5)
        ]
        self.subtasks = [
            Subtask.objects.create(
                title=f'Subtask #{i}',
                order=i,
                task=self.tasks[0],
                done=(i % 2 == 0)
            ) for i in range(0, 2)
        ]

    def test_success(self):
        response = self.client.get(f'{self.endpoint}{self.boards[0].id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('id'), self.boards[0].id)

        # column assertions
        columns = response.data.get('columns')
        self.assertEqual(len(columns), 4)
        for i in range(0, 4):
            self.assertEqual(columns[i].get('id'), self.columns[i].id)
            self.assertEqual(columns[i].get('order'), self.columns[i].order)

        # task assertions
        tasks = columns[0].get('tasks')
        self.assertEqual(len(tasks), 5)
        for i in range(0, 5):
            self.assertEqual(tasks[i].get('id'), self.tasks[i].id)
            self.assertEqual(tasks[i].get('title'), self.tasks[i].title)
            self.assertEqual(tasks[i].get('description'),
                             self.tasks[i].description)
            self.assertEqual(tasks[i].get('order'), self.tasks[i].order)
            self.assertEqual(tasks[i].get('user'), self.tasks[i].user.username)

        # subtask assertions
        subtasks = tasks[0].get('subtasks')
        self.assertEqual(len(subtasks), 2)
        for i in range(0, 2):
            self.assertEqual(subtasks[i].get('id'), self.subtasks[i].id)
            self.assertEqual(subtasks[i].get('title'), self.subtasks[i].title)
            self.assertEqual(subtasks[i].get('order'), self.subtasks[i].order)
            self.assertEqual(subtasks[i].get('done'), self.subtasks[i].done)

    def test_board_id_blank(self):
        response = self.client.get(self.endpoint,
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID cannot be empty.',
                                    code='blank')
        })

    def test_board_invalid(self):
        response = self.client.get(f'{self.endpoint}aksdj',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID must be a number.',
                                    code='invalid')
        })

    def test_board_not_found(self):
        response = self.client.get(f'{self.endpoint}1231241',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board not found.',
                                    code='not_found')
        })

    def test_auth_token_empty(self):
        response = self.client.get(f'{self.endpoint}{self.boards[0].id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_token_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.boards[0].id}',
                                   HTTP_AUTH_USER=self.member['username'],
                                   HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfos')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_user_blank(self):
        response = self.client.get(f'{self.endpoint}{self.boards[0].id}',
                                   HTTP_AUTH_USER='',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_auth_user_invalid(self):
        response = self.client.get(f'{self.endpoint}{self.boards[0].id}',
                                   HTTP_AUTH_USER='invalidio',
                                   HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)

    def test_wrong_team(self):
        initial_count = Board.objects.count()
        response = self.client.get(
            f'{self.endpoint}{self.boards[0].id}',
            HTTP_AUTH_USER=self.wrong_team_member['username'],
            HTTP_AUTH_TOKEN=self.wrong_team_member['token'],
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authenticated_response.data)
        self.assertEqual(Board.objects.count(), initial_count)

    def test_wrong_board(self):
        initial_count = Board.objects.count()
        response = self.client.get(
            f'{self.endpoint}{self.boards[0].id}',
            HTTP_AUTH_USER=self.wrong_board_member['username'],
            HTTP_AUTH_TOKEN=self.wrong_board_member['token'],
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, not_authorized_response.data)
        self.assertEqual(Board.objects.count(), initial_count)
