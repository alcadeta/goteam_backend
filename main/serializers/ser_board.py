from rest_framework import serializers
from ..models import Board


class BoardSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=35,
        error_messages={
            'blank': 'Board name cannot be empty.',
        }
    )

    class Meta:
        model = Board
        fields = ('id', 'team', 'name')
