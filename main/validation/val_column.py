from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from ..models import Column


# return (column, response)
def validate_column_id(column_id):
    if not column_id:
        return None, Response({
            'column_id': ErrorDetail(string='Column ID cannot be empty.',
                                     code='blank')
        }, 400)

    try:
        int(column_id)
    except ValueError:
        return None, Response({
            'column_id': ErrorDetail(string='Column ID must be a number.',
                                     code='invalid')
        }, 400)

    try:
        column = Column.objects.get(id=column_id)
    except Column.DoesNotExist:
        return None, Response({
            'column_id': ErrorDetail(string='Column not found.',
                                     code='not_found')
        }, 404)

    return column, None

