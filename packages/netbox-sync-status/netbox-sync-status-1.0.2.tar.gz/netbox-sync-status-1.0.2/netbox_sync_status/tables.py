import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from .models import SyncStatus, SyncSystem


class SyncStatusListTable(NetBoxTable):
    actions = columns.ActionsColumn(
        actions=()
    )

    device = tables.Column(
        linkify=True
    )

    system = tables.Column(
        linkify=True
    )
    class Meta(NetBoxTable.Meta):
        model = SyncStatus
        fields = ("device", "status", "system", "message", "created")


class SyncSystemListTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )

    tags = columns.TagColumn(
        url_name="plugins:netbox_sync_status:syncsystem_list"
    )

    class Meta(NetBoxTable.Meta):
        model = SyncSystem
        fields = ("name", "description", "tags")