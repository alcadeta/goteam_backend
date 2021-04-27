from main.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
import bcrypt


not_authenticated_response = Response({
    'auth': ErrorDetail(string="Authentication failure.",
                        code='not_authenticated')
}, 403)


# return (team id, response)
def authenticate(username, token):
    try:
        user = User.objects.get(username=username)
    except (User.DoesNotExist, ValueError):
        return None, not_authenticated_response

    try:
        tokens_match = bcrypt.checkpw(
            bytes(user.username, 'utf-8') + user.password,
            bytes(token, 'utf-8'))
        if not tokens_match:
            return None, not_authenticated_response
    except ValueError:
        return None, not_authenticated_response

    return user, None


not_authorized_response = Response({
    'auth': ErrorDetail(string='Authorization failure.',
                        code='not_authorized')
}, 403)


# return response
def authorize(username):
    try:
        user = User.objects.get(username=username)
        if not user.is_admin:
            return not_authorized_response
    except User.DoesNotExist:
        return not_authorized_response
