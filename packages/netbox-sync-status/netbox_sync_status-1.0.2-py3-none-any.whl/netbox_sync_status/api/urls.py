from netbox.api.routers import NetBoxRouter
from . import views
from django.urls import path


app_name = "netbox_sync_status"

router = NetBoxRouter()
router.register("sync-status", views.SyncStatusViewSet)
router.register("sync-system", views.SyncSystemViewSet)

urlpatterns = router.urls + [
      path("sync-device/<int:pk>/", views.DeviceSyncView.as_view(), name='sync-device'),
]


