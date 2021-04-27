from rest_framework import serializers
from main.models import Team, User
import bcrypt


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=5,
        max_length=35,
        error_messages={
            'blank': 'Username cannot be empty.',
            'max_length': 'Username cannot be longer than 35 characters.'
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=255,
        error_messages={
            'blank': 'Password cannot be empty.',
            'max_length': 'Password cannot be longer than 255 characters.'
        }
    )
    # Doesn't need min/max-length since we only care whether it matches the
    # password or not. If it does, min/max-length is validated since the
    # password will already be validated.
    password_confirmation = serializers.CharField(required=False)
    team = serializers.IntegerField(required=False)
    invite_code = serializers.UUIDField(
        required=False,
        error_messages={'invalid': 'Invalid invite code.'}
    )

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        invite_code = data.get('invite_code')
        if invite_code:
            try:
                data['team'] = Team.objects.get(invite_code=invite_code)
            except Team.DoesNotExist:
                raise serializers.ValidationError({
                    'invite_code': 'Team not found.'
                })
            data['is_admin'] = False
            data.pop('invite_code')
        else:
            data['is_admin'] = True
        return super().validate(data)

    def create(self, validated_data):
        password_confirmation = validated_data.get('password_confirmation')
        if not password_confirmation:
            raise serializers.ValidationError({
                'password_confirmation': 'Password confirmation cannot be '
                                         'empty.'
            }, 'blank')

        if password_confirmation != validated_data.get('password'):
            raise serializers.ValidationError({
                'password_confirmation':
                    'Confirmation must match the password.'
            }, 'no_match')

        if validated_data.get('is_admin') and not validated_data.get('team'):
            validated_data['team'] = Team.objects.create()

        validated_data['password'] = bcrypt.hashpw(
            bytes(validated_data['password'], 'utf-8'),
            bcrypt.gensalt()
        )

        validated_data.pop('password_confirmation')
        return User.objects.create(**validated_data)
