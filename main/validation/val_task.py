from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from ..models import Task


# return (task, response)
def validate_task_id(task_id):
    if not task_id:
        return None, Response({
            'task_id': ErrorDetail(string='Task ID cannot be empty.',
                                   code='blank')
        }, 400)

    try:
        int(task_id)
    except ValueError:
        return None, Response({
            'task_id': ErrorDetail(string='Task ID must be a number.',
                                   code='invalid')
        }, 400)

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return None, Response({
            'task_id': ErrorDetail(string='Task not found.',
                                   code='not_found')
        }, 404)

    return task, None

