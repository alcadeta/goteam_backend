from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from ..models import Board


# return (board, response)
def validate_board_id(board_id):
    if not board_id:
        return None, Response({
            'board_id': ErrorDetail(string='Board ID cannot be empty.',
                                    code='blank')
        }, 400)

    try:
        int(board_id)
    except ValueError:
        return None, Response({
            'board_id': ErrorDetail(string='Board ID must be a number.',
                                    code='invalid')
        }, 400)

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return None, Response({
            'board_id': ErrorDetail(string='Board not found.',
                                    code='not_found')
        }, 404)

    return board, None

