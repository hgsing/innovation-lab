import json
import tomlkit
try:
    import tomllib as tomli  # type: ignore
except ModuleNotFoundError:
    import tomli

from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .state import devices, skill_boss
from . import state

# Create your views here.

def index(request: HttpRequest):
    return render(
        request,
        "home.html",
        {
            "devices": [device.to_attr_dict() for device in devices.values()]
        },
    )


def manual_control(request: HttpRequest):
    return render(
        request,
        "manual_control.html",
        {
            "init_conn": skill_boss.connected,
        },
    )


@require_POST
def get_tags(request: HttpRequest):
    if not skill_boss:
        return render(request, "error.html", {"error": "Problem displaying PLC data."})

    return JsonResponse({"data": skill_boss.data, "connection": skill_boss.connected})


def device_data(request: HttpRequest, device_id: str):
    device = devices.get(device_id)

    if device is None:
        return render(request, "error.html", {"error": "Device not found"})

    return render(
        request,
        "device.html",
        {
            "device": device.to_attr_dict(),
            "headers": device.get_data_value_headings(),
            "data": device.data,
        },
    )


def table(request, device_id):
    device = devices.get(device_id)

    if not device:
        return HttpResponse("Error: no table for device " + device_id + ".")

    return render(
        request,
        "table.html",
        {
            "headers": device.get_data_value_headings(),
            "data": device.data,
        },
    )


def control_panel(request: HttpRequest):
    return render(request, "control_panel.html")


@require_POST
def set_logging(request: HttpRequest):

    if "logging" in request.POST.keys():
        if not request.POST["logging"] == "false":
            state.enable_logging()
            return JsonResponse({"logging": True})
        else:
            state.disable_logging()
            return JsonResponse({"logging": False})

    return JsonResponse({"logging": "error in request"})


@require_POST
def reconnect_devices(request: HttpRequest):

    state.connect_devices()
    return HttpResponse("ok")


def raw(request: HttpRequest, device_id):
    device = devices.get(device_id)

    if not device:
        return HttpResponse("Raw view error: device " + device_id + " not found.")

    return JsonResponse({"tags": device.data, "connection": device.connected})


@require_POST
def send_command(request, cmd: str, value: str = None):

    if skill_boss.connected:
        skill_boss.send_command(cmd, value)
        return HttpResponse("ok")
    else:
        skill_boss.disconnect()
        skill_boss.connect()
        return HttpResponse("error")


def view_faults(request: HttpRequest):
    with open(state.fault_file, mode="rb") as fp:
        fault_list = tomli.load(fp)
        faults = fault_list["faults"] if fault_list else {}

    return render(request, "faults.html", context={"faults": json.dumps(faults)})


@require_POST
def save_faults(request: HttpRequest):
    items = str(request.body, "utf-8").strip()
    saved = json.loads(items)

    for item in saved:
        item.pop("key")

    save_format = {}
    save_format["faults"] = saved

    with open(state.fault_file, "wt", encoding="utf-8") as ff:
        tomlkit.dump(save_format, ff)

    return HttpResponse("ok")
