from netbox.views import generic
from dcim.models import Device
from netbox_sync_status.filtersets import SyncStatusFilterForm, SyncStatusFilterSet
from .tables import SyncStatusListTable, SyncSystemListTable
from .models import SyncStatus, SyncSystem
from .forms import SyncSystemForm
from utilities.views import GetReturnURLMixin
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib import messages
from extras.webhooks import enqueue_object
from extras.choices import ObjectChangeActionChoices
from netbox.context import webhooks_queue


class SyncSystemView(generic.ObjectView):
    queryset = SyncSystem.objects.prefetch_related("tags")


class SyncSystemListView(generic.ObjectListView):
    queryset = SyncSystem.objects.prefetch_related("tags")
    table = SyncSystemListTable


class SyncSystemEditView(generic.ObjectEditView):
    queryset = SyncSystem.objects.all()
    form = SyncSystemForm


class SyncSystemDeleteView(generic.ObjectDeleteView):
    queryset = SyncSystem.objects.all()


class SyncStatusListView(generic.ObjectListView):
    queryset = SyncStatus.objects.order_by("-id")
    table = SyncStatusListTable
    filterset = SyncStatusFilterSet
    filterset_form = SyncStatusFilterForm
    actions = ("export")


class DeviceSyncView(GetReturnURLMixin, View):
    queryset = Device.objects.all()

    def post(self, request, **kwargs):
        selected_objects = self.queryset.filter(
            pk=kwargs.get("pk"),
        )

        for obj in selected_objects:
            queue = webhooks_queue.get()
            enqueue_object(queue, obj, request.user, request.id, ObjectChangeActionChoices.ACTION_UPDATE)
            webhooks_queue.set(queue)

        messages.success(request, f"Manual sync started for {obj.name}")
        return redirect(self.get_return_url(request))