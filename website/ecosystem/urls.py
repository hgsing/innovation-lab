from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('devices/<device_id>', views.device_data_display, name='device-data-display'),
    path('get_tags', csrf_exempt(views.get_tags), name='get-tags'),
    path('tables/<device_id>', views.table, name='table'),
    path('raw/<device_id>',views.raw, name='raw'),
    path('control_panel', views.control_panel, name='control-panel'),
    path('set_logging', csrf_exempt(views.set_logging), name='set-logging'),
    path('reconnect-devices', csrf_exempt(views.reconnect_devices), name='reconnect-devices'),
    path('manual_control', views.manual_control, name='manual-control'),
    path('command/<cmd>', csrf_exempt(views.send_command), name='send-command'),
    path('command/<cmd>/<value>', csrf_exempt(views.send_command), name='send-command'),
    path('view_faults', views.view_faults, name='view-faults'),
    path('save_faults', csrf_exempt(views.save_faults), name='save-faults'),
    path("robots.txt", views.plain_text, name='robots'),
    path("humans.txt", TemplateView.as_view(template_name="humans.txt", content_type="text/plain")),
]
