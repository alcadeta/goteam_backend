from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..validation.val_auth import \
    authenticate, authorize, not_authenticated_response
from ..validation.val_team import validate_team_id


@api_view(['GET'])
def teams(request):
    auth_user = request.META.get('HTTP_AUTH_USER')
    auth_token = request.META.get('HTTP_AUTH_TOKEN')

    user, authentication_response = authenticate(auth_user, auth_token)
    if authentication_response:
        return authentication_response

    authorization_response = authorize(auth_user)
    if authorization_response:
        return authorization_response

    team_id = request.query_params.get('team_id')

    team, validation_response = validate_team_id(team_id)
    if validation_response:
        return validation_response
    if team.id != user.team.id:
        return not_authenticated_response

    return Response({
        'id': team.id,
        'inviteCode': team.invite_code
    }, 200)


