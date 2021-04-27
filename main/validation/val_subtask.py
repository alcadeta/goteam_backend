from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from ..models import Subtask


def validate_subtask_id(subtask_id):
    if not subtask_id:
        return None, Response({
            'id': ErrorDetail(string='Subtask ID cannot be empty.',
                              code='blank')
        }, 400)
    try:
        subtask = Subtask.objects.get(id=subtask_id)
    except Subtask.DoesNotExist:
        return None, Response({
            'id': ErrorDetail(string='Subtask not found.',
                              code='not_found')
        })

    return subtask, None
