from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from netbox.api.serializers import NetBoxModelSerializer
from ..models import SyncStatus, SyncSystem


#
# Regular serializers
#

class SyncStatusSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_sync_status-api:syncstatus-detail"
    )

    class Meta:
        model = SyncStatus
        fields = (
            "created", "url", "device", "system", "status", "message"
        )


class SyncSystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_sync_status-api:syncsystem-detail"
    )

    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return obj.name

    class Meta:
        model = SyncSystem
        fields = (
            "id", "created", "url", "name", "display", "description", "tags"
        )


class SyncSystemDeviceStatusSerializer(serializers.Serializer):
    device_name = serializers.CharField()
    status = serializers.CharField()
