import django_filters
from django import forms
from netbox.filtersets import BaseFilterSet
from django.utils.translation import gettext as _
from .models import SyncStatus, SyncSystem
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import DynamicModelMultipleChoiceField
from dcim.models import Device

from netbox.forms import NetBoxModelFilterSetForm


class SyncStatusFilterForm(NetBoxModelFilterSetForm):
    model = SyncStatus

    system = DynamicModelMultipleChoiceField(
        queryset=SyncSystem.objects.all(),
        required=False,
        label=_("System")
    )

    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device")
    )

    show_last_sync_only = forms.NullBooleanField(
        required=False,
        label="Show last sync only for each device/system only",
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class SyncStatusFilterSet(BaseFilterSet):
    class Meta:
        model = SyncStatus
        fields = ("system", "device", "status", "message", "is_latest")


    def search(self, queryset, name, value):
        return queryset.filter(device__name__icontains=value)