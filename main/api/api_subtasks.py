from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from ..models import Subtask
from ..serializers.ser_subtask import SubtaskSerializer
from ..validation.val_auth import \
    authenticate, authorize, not_authenticated_response
from ..validation.val_task import validate_task_id
from ..validation.val_subtask import validate_subtask_id


@api_view(['GET', 'PATCH'])
def subtasks(request):
    username = request.META.get('HTTP_AUTH_USER')
    token = request.META.get('HTTP_AUTH_TOKEN')

    user, authentication_response = authenticate(username, token)
    if authentication_response:
        return authentication_response

    if request.method == 'GET':
        task_id = request.query_params.get('task_id')

        task, validation_response = validate_task_id(task_id)
        if validation_response:
            return validation_response

        if task.column.board.team.id != user.team.id:
            return not_authenticated_response

        task_subtasks = Subtask.objects.filter(task_id=task_id)
        serializer = SubtaskSerializer(task_subtasks, many=True)
        return Response({
            'subtasks': list(
                map(
                    lambda st: {
                        'id': st['id'],
                        'order': st['order'],
                        'title': st['title'],
                        'done': st['done']
                    },
                    serializer.data
                )
            )
        }, 200)

    if request.method == 'PATCH':
        subtask_id = request.query_params.get('id')
        subtask, validation_response = validate_subtask_id(subtask_id)
        if validation_response:
            return validation_response

        authorization_response = authorize(username)
        if authorization_response and subtask.task.user != user:
            return authorization_response

        if subtask.task.column.board.team.id != user.team.id:
            return not_authenticated_response

        if not request.data:
            return Response({
                'data': ErrorDetail(string='Data cannot be empty.',
                                    code='blank')
            }, 400)

        if 'title' in request.data.keys() and not request.data.get('title'):
            return Response({
                'title': ErrorDetail(string='Title cannot be empty.',
                                     code='blank')
            }, 400)

        done = request.data.get('done')
        if 'done' in request.data.keys() and (done == '' or done is None):
            return Response({
                'done': ErrorDetail(string='Done cannot be empty.',
                                    code='blank')
            }, 400)

        order = request.data.get('order')
        if 'order' in request.data.keys() and (order == '' or order is None):
            return Response({
                'order': ErrorDetail(string='Order cannot be empty.',
                                     code='blank')
            }, 400)

        serializer = SubtaskSerializer(Subtask.objects.get(id=subtask_id),
                                       data=request.data,
                                       partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        subtask = serializer.save()
        return Response({
            'msg': 'Subtask update successful.',
            'id': subtask.id
        }, 200)

