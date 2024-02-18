from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .viewsets import selinuxAPIview
from .views import host_message_sugestion, selinux_list, message_list, suggestion_list, SetroubleshootEntry_list_full

router = routers.DefaultRouter()
router.register('host', selinuxAPIview)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('selinux_list/', selinux_list),
    path('api/', include(router.urls)),
]
