from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_sync_status:syncsystem_list",
        link_text="Sync Systems",
        buttons=[
            PluginMenuButton(
                link="plugins:netbox_sync_status:syncsystem_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN
            )
        ]
    ),
)