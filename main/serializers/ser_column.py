from rest_framework.serializers import ModelSerializer
from ..models import Column


class ColumnSerializer(ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'
