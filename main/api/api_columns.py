from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from ..models import Column, Task
from ..serializers.ser_column import ColumnSerializer
from ..serializers.ser_task import TaskSerializer
from ..validation.val_auth import \
    authenticate, authorize, not_authenticated_response
from ..validation.val_board import validate_board_id
from ..validation.val_column import validate_column_id


@api_view(['GET', 'PATCH'])
def columns(request):
    username = request.META.get('HTTP_AUTH_USER')
    token = request.META.get('HTTP_AUTH_TOKEN')

    user, authentication_response = authenticate(username, token)
    if authentication_response:
        return authentication_response

    if request.method == 'GET':
        board_id = request.query_params.get('board_id')
        board, validation_response = validate_board_id(board_id)
        if validation_response:
            return validation_response
        if board.team.id != user.team.id:
            return not_authenticated_response

        board_columns = Column.objects.filter(board_id=board_id)
        if not board_columns:
            board_columns = [
                Column.objects.create(
                    order=i,
                    board_id=board_id
                ) for i in range(0, 4)
            ]

        serializer = ColumnSerializer(board_columns, many=True)
        return Response({
            'columns': list(
                map(lambda column: {'id': column['id'], 'order': column['order']},
                    serializer.data)
            )
        }, 200)

    if request.method == 'PATCH':
        authorization_response = authorize(username)

        column_id = request.query_params.get('id')
        column, validation_response = validate_column_id(column_id)
        if validation_response:
            return validation_response
        if column.board.team.id != user.team.id:
            return not_authenticated_response

        for task in request.data:
            try:
                task_id = task.pop('id')
            except KeyError:
                return Response({
                    'task.id': ErrorDetail(string='Task ID cannot be empty.',
                                           code='blank')
                }, 400)

            existing_task = Task.objects.get(id=task_id)

            if authorization_response \
                    and task['user'] != user.username \
                    and column.id != existing_task.column.id:
                return authorization_response

            serializer = TaskSerializer(existing_task,
                                        data={**task, 'column': column.id},
                                        partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, 400)

            serializer.save()

        return Response({
            'msg': 'Column and all its tasks updated successfully.',
            'id': column.id,
        }, 200)
