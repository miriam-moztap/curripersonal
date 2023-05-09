# Rest Framework
from rest_framework import serializers

# Models
from ..general.models import CVLanguage


class CVLanguageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVLanguage
        fields = (
            'id',
            'language',
        )

class CVLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVLanguage
        fields = '__all__'