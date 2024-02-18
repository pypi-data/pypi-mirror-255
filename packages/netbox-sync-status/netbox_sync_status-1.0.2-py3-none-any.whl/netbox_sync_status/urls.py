from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from .models import SyncSystem
from . import views


urlpatterns = (
    path("sync-device/<int:pk>/", views.DeviceSyncView.as_view(), name="sync_device"),
    path("sync-status/", views.SyncStatusListView.as_view(), name="syncstatus_list_device"),
    path("sync-system/", views.SyncSystemListView.as_view(), name="syncsystem_list"),
    path("sync-system/add/", views.SyncSystemEditView.as_view(), name="syncsystem_add"),
    path("sync-system/<int:pk>/", views.SyncSystemView.as_view(), name="syncsystem"),
    path("sync-system/<int:pk>/edit/", views.SyncSystemEditView.as_view(), name="syncsystem_edit"),
    path("sync-system/<int:pk>/delete/", views.SyncSystemDeleteView.as_view(), name="syncsystem_delete"),
    path("sync-system/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="syncsystem_changelog", kwargs={
        "model": SyncSystem
    }),
)