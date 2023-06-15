import json
import tomlkit
try:
    import tomllib as tomli  # type: ignore
except ModuleNotFoundError:
    import tomli

from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST, require_safe

from .state import devices, skill_boss
from . import state

# Create your views here.


@require_GET
def index(request: HttpRequest):
    return render(
        request,
        "home.html",
        {
            "devices": [device.to_attr_dict() for device in devices.values()]
        },
    )


@require_GET
def plain_text(request):
    lines = [
        "User-Agent: *",
        "Disallow: /private/",
        "Disallow: /junk/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_GET
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


@require_GET
def device_data_display(request: HttpRequest, device_id: str):
    device = devices.get(device_id)

    if device is None:
        return render(request, "error.html", {"error": "Device not found"})

    if not device.connected:
        render(
            request,
            "device-data-display.html",
            {"device": device.to_attr_dict(), "headers": None},
        )

    return render(
        request,
        "device-data-display.html",
        {
            "device": device.to_attr_dict(),
            "headers": device.get_data_value_headings(),
            "data": device.data,
        },
    )


@require_GET
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


@require_GET
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
    return HttpResponse("success")


@require_safe
def raw(request: HttpRequest, device_id):
    device = devices.get(device_id)

    if not device:
        return HttpResponse("Raw view error: device " + device_id + " not found.")

    return JsonResponse({"tags": device.data, "connection": device.connected})


@require_POST
def send_command(request, cmd: str, value: str = ""):

    if cmd in commands:
        tags = " ".join(["tag", "write", *commands[cmd]])
    else:
        tags = "tag write " + cmd

    if value:
        tags = " ".join([tags.strip(), value])

    if skill_boss.connected:
        skill_boss.send(tags)
        return HttpResponse("sent")
    else:
        skill_boss.disconnect()
        skill_boss.connect()
        return HttpResponse("not sent")


commands: dict[str, list[str]] = {
    "system_start": ["SystemStartPB 1 SystemStopPB 0 System_Pause 0"],
    "system_stop": ["SystemStartPB 0 SystemStopPB 1 System_Pause 0"],
    "system_pause": ["SystemStartPB 0 SystemStopPB 0 System_Pause 1"],
    "cycle_stop": ["CycleStopPB 1"],
    "master_speed": ["MasterSpdSetting"],
    "induction_roller_on": [
        "InductionRoller1_ManRunPB 1",
        "InductionRoller1_ManStopPB 0",
    ],
    "induction_roller_off": [
        "InductionRoller1_ManRunPB 0",
        "InductionRoller1_ManStopPB 1",
        "InductionRoller1_Jog 0",
    ],
    "induction_roller_jog": [
        "InductionRoller1_ManRunPB 0",
        "InductionRoller1_Jog 1",
        "InductionRoller1_ManStopPB 0",
    ],
    "induction_roller_speed": ["InductionRollerSpdOffset"],
    "induction_conveyor_on": [
        "InductionConveyor_ManRunPB 1",
        "InductionConveyor_ManStopPB 0",
    ],
    "induction_conveyor_off": [
        "InductionConveyor_ManRunPB 0",
        "InductionConveyor_ManStopPB 1",
        "InductionConveyor_FwdJog 0",
    ],
    "induction_conveyor_jog": [
        "InductionConveyor_ManStopPB 0",
        "InductionConveyor_FwdJog 1",
    ],
    "induction_conveyor_speed": ["InductionConveyorSpdOffset"],
    "vertical_conveyor_on": [
        "VerticalSorterConveyor_ManRunPB 1",
        "VerticalSorterConv_ManStopPB 0",
    ],
    "vertical_conveyor_off": [
        "VerticalSorterConveyor_ManRunPB 0",
        "VerticalSorterConv_ManStopPB 1",
        "VerticalSorterConveyor_Jog 0",
    ],
    "vertical_conveyor_jog": [
        "VerticalSorterConv_ManStopPB 0",
        "VerticalSorterConveyor_Jog 1",
    ],
    "vertical_conveyor_raise": [
        "VerticalSorterConveyor_ManRunPB 0",
        "VerticalSorterConv_ManStopPB 1",
        "VerticalSorterConveyor_Jog 0",
        "VerticalSorterConveyor_RaisePB 1",
        "VerticalSorterConv_LowerPB 0",
    ],
    "vertical_conveyor_lower": [
        "VerticalSorterConveyor_ManRunPB 0",
        "VerticalSorterConv_ManStopPB 1",
        "VerticalSorterConveyor_Jog 0",
        "VerticalSorterConveyor_RaisePB 0",
        "VerticalSorterConv_LowerPB 1",
    ],
    "rework_conveyor_on": ["ReworkConveyor_ManStopPB 0", "ReworkConveyor_ManRunPB 1"],
    "rework_conveyor_off": [
        "ReworkConveyor_ManRunPB 0",
        "ReworkConveyor_ManStopPB 1",
        "ReworkConveyor_Jog 0",
    ],
    "rework_conveyor_jog": [
        "ReworkConveyor_ManStopPB 0",
        "ReworkConveyor_Jog 1",
    ],
    "distribution_conveyor_on": [
        "DistributionConv_ManRunPB 1",
        "DistributionConv_ManStopPB 0",
        "DistributionConveyor_RevJog 0",
        "DistributionConveyor_FwdJog 0",
    ],
    "distribution_conveyor_off": [
        "DistributionConv_ManRunPB 0",
        "DistributionConv_ManStopPB 1",
        "DistributionConveyor_RevJog 0",
        "DistributionConveyor_FwdJog 0",
    ],
    "distribution_conveyor_fjog": [
        "DistributionConv_ManRunPB 0",
        "DistributionConv_ManStopPB 0",
        "DistributionConveyor_FwdJog 1",
        "DistributionConveyor_RevJog 0",
    ],
    "distribution_conveyor_rjog": [
        "DistributionConv_ManRunPB 0",
        "DistributionConv_ManStopPB 0",
        "DistributionConveyor_FwdJog 0",
        "DistributionConveyor_RevJog 1",
    ],
    "distribution_conveyor_speed": ["DistributionConveyorSetSpeedFPM"],
    "diverter_1_on": [
        "Sorter1_DivertToTray 1",
        "Sorter1_DivertToTrayPB 1",
    ],
    "diverter_1_off": [
        "Sorter1_DivertToTray 0",
        "Sorter1_DivertToTrayPB 0",
    ],
    "diverter_2_on": [
        "Sorter2_DivertToTray 1",
        "Sorter2_DivertToTrayPB 1",
    ],
    "diverter_2_off": [
        "Sorter2_DivertToTray 0",
        "Sorter2_DivertToTrayPB 0",
    ],
    "diverter_3_raise": ["PickandPlace_RaisePB 1", "PickandPlace_LowerPB 0"],
    "diverter_3_lower": ["PickandPlace_LowerPB 1", "PickandPlace_RaisePB 0"],
    "diverter_3_extend": [
        "PickandPlace_MoveToTrayPB 1",
        "PickandPlace_MoveToConveyorPB 0",
    ],
    "diverter_3_retract": [
        "PickandPlace_MoveToConveyorPB 1",
        "PickandPlace_MoveToTrayPB 0",
    ],
    "diverter_3_off": ["PickandPlace_ManualVacuum 0"],
    "diverter_3_on": ["PickandPlace_ManualVacuum 1"],
}


@require_GET
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

    return HttpResponse("200")
