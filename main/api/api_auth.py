from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
import bcrypt

from ..serializers.ser_user import UserSerializer
from ..models import User


@api_view(['POST'])
def register(request):
    invite_code = request.query_params.get('invite_code')

    data = {
        'username': request.data.get('username'),
        'password': request.data.get('password'),
        'password_confirmation': request.data.get('password_confirmation'),
        'invite_code': invite_code
    } if invite_code else request.data

    serializer = UserSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, 400)
    user = serializer.save()

    return Response({
        'msg': 'Registration successful.',
        'username': user.username,
        'token': bcrypt.hashpw(
            bytes(user.username, 'utf-8') + user.password,
            bcrypt.gensalt()
        ).decode('utf-8'),
        'teamId': user.team_id,
        'isAdmin': user.is_admin
    }, 201)


@api_view(['POST'])
def login(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, 400)

    try:
        user = User.objects.get(username=request.data.get('username'))
    except User.DoesNotExist:
        return Response({
            'username': ErrorDetail(string='Invalid username.', code='invalid')
        }, 400)

    pw_bytes = bytes(request.data.get('password'), 'utf-8')
    if not bcrypt.checkpw(pw_bytes, bytes(user.password)):
        return Response({
            'password': ErrorDetail(string='Invalid password.', code='invalid')
        }, 400)

    return Response({
        'msg': 'Login successful.',
        'username': user.username,
        'token': bcrypt.hashpw(
            bytes(user.username, 'utf-8') + user.password,
            bcrypt.gensalt()
        ).decode('utf-8'),
        'teamId': user.team_id,
        'isAdmin': user.is_admin,
    }, 200)


@api_view(['POST'])
def verify_token(request):
    failure_response = Response({'msg': 'Token verification failure.'}, 400)
    try:
        user = User.objects.get(username=request.data.get('username'))
        valid_token = bytes(user.username, 'utf-8') + user.password
        request_token_raw = request.data.get('token')
        request_token = bytes(request_token_raw, 'utf-8')
        match = bcrypt.checkpw(valid_token, request_token)
        if not match:
            return failure_response
    except (ValueError, User.DoesNotExist):
        return failure_response

    return Response({
        'msg': 'Token verification success.',
        'username': user.username,
        'teamId': user.team_id,
        'isAdmin': user.is_admin,
    }, 200)
