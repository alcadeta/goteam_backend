from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from ..models import User


# return (user, response)
def validate_username(username):
    if not username:
        return None, Response({
            'username': ErrorDetail(string='Username cannot be empty.',
                                    code='blank')
        }, 400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None, Response({
            'username': ErrorDetail(string='User not found.',
                                    code='not_found')
        }, 404)

    return user, None


# return (is_active, response)
def validate_is_active(is_active):
    is_empty_response = Response({
        'is_active': ErrorDetail(string='Is Active cannot be empty.',
                                 code='blank')
    }, 400)

    try:
        if not str(is_active):
            return None, is_empty_response
    except ValueError:
        return None, is_empty_response

    if not isinstance(is_active, bool):
        return None, Response({
            'is_active': ErrorDetail(string='Is Active must be a boolean.',
                                     code='invalid')
        }, 400)

    return is_active, None
