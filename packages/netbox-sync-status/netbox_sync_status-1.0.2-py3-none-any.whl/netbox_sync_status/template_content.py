from extras.plugins import PluginTemplateExtension
from netbox_sync_status.models import SyncSystem


class DeviceSync(PluginTemplateExtension):
    model = "dcim.device"

    def buttons(self):
        return self.render(
            "netbox_sync_status/sync_status_buttons.html",
        )

    def right_page(self):
        sync_systems = SyncSystem.objects.all()
        sync_status = self.context["object"].sync_status.order_by("system", "-id").filter(is_latest=True)

        items = []
        for system in sync_systems:
            data = {
                "system": system,
                "last_event": None
            }

            events = [event for event in sync_status if event.system.name == system.name]
            if len(events) > 0:
                data["last_event"] = events[0]
            
            items.append(data)

        return self.render(
            "netbox_sync_status/sync_status.html",
            extra_context={"sync_systems": items},
        )


template_extensions = [DeviceSync]
