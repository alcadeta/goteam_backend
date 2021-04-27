from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from ..models import User
from ..validation.val_auth import \
    authenticate, authorize, not_authenticated_response, \
    not_authorized_response
from ..validation.val_team import validate_team_id
from ..validation.val_board import validate_board_id
from ..validation.val_user import validate_username, validate_is_active


@api_view(['GET', 'POST', 'DELETE'])
def users(request):
    auth_user = request.META.get('HTTP_AUTH_USER')
    auth_token = request.META.get('HTTP_AUTH_TOKEN')

    auth_user, authentication_response = authenticate(auth_user, auth_token)
    if authentication_response:
        return authentication_response

    if request.method == 'GET':
        request_team_id = request.query_params.get('team_id')
        team, validation_response = validate_team_id(request_team_id)
        if validation_response:
            return validation_response
        if team.id != auth_user.team.id:
            return not_authenticated_response

        members = User.objects.filter(team_id=team.id)

        if 'board_id' in request.query_params.keys():
            board_id = request.query_params.get('board_id')
            board, validation_response = validate_board_id(board_id)
            if validation_response:
                return validation_response

            board_members = User.objects.filter(board=board)

            return Response(list(map(
                lambda member: {'username': member.username,
                                'isActive': member in board_members,
                                'isAdmin': member.is_admin},
                members
            )), 200)

        return Response(list(map(
            lambda member: {'username': member.username,
                            'isActive': None,
                            'isAdmin': member.is_admin},
            members
        )), 200)

    if request.method == 'POST':
        authorization_response = authorize(auth_user.username)
        if authorization_response:
            return authorization_response

        username = request.data.get('username')
        user, validation_response = validate_username(username)
        if validation_response:
            return validation_response
        if user.team.id != auth_user.team.id:
            return not_authorized_response

        board_id = request.data.get('board_id')
        board, validation_response = validate_board_id(board_id)
        if validation_response:
            return validation_response

        is_active = request.data.get('is_active')
        is_active, validation_response = validate_is_active(is_active)
        if validation_response:
            return validation_response

        if is_active:
            board.user.add(user)
        else:
            board.user.remove(user)

        return Response(
            {'msg': f'{user.username} is removed from {board.name}.'},
            200
        )

    if request.method == 'DELETE':
        authorization_response = authorize(auth_user.username)
        if authorization_response:
            return authorization_response

        username = request.query_params.get('username')
        user, validation_response = validate_username(username)
        if validation_response:
            return validation_response
        if user.team.id != auth_user.team.id:
            return not_authorized_response

        # this is not authorization. it checks whether the user that is up for
        # deletion is admin
        if user.is_admin:
            return Response({
                'username': ErrorDetail(
                    string='Team leaders cannot be deleted from their teams.',
                    code='forbidden'
                )
            }, 403)

        user.delete()

        return Response({
            'msg': 'Member has been deleted successfully.',
        }, 200)
