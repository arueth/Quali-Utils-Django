from rest_framework import serializers

from resource.models import Family, Model


class ResourceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ('id', 'family', 'name', 'description')


class ResourceFamilySerializer(serializers.ModelSerializer):
    models = ResourceModelSerializer(many=True, read_only=True)

    class Meta:
        model = Family
        fields = ('id', 'name', 'description', 'models')
