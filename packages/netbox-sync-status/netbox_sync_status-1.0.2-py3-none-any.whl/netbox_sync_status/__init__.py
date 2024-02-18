from extras.plugins import PluginConfig
from .version import __version__


class NetBoxSyncStatusConfig(PluginConfig):
    name = "netbox_sync_status"
    verbose_name = "NetBox Sync Status"
    description = "Shows the current sync status towards external systems"
    version = __version__
    author = "Patrick Falk Nielsen"
    author_email = "panie@jysk.com"
    required_settings = []


config = NetBoxSyncStatusConfig # noqa E305
