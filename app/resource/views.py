from rest_framework import viewsets

from resource.models import Family, Model
from resource.serializers import ResourceFamilySerializer, ResourceModelSerializer


class ResourceFamilyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows resource families to be viewed
    """
    queryset = Family.objects.all()
    serializer_class = ResourceFamilySerializer


class ResourceModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows resource models to be viewed
    """
    queryset = Model.objects.all()
    serializer_class = ResourceModelSerializer
