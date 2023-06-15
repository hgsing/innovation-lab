var MainMenu = {
  name: "MainMenu",
  buttons: [
    {
      name: "SystemStart",
      color: "green",
      cmd: "system_start",
      text: "System Start",
    },
    {
      name: "LineSpeed",
      color: "gray",
      cmd: null,
      text: "Line Speed",
    },
    {
      name: "SystemPause",
      color: "yellow",
      cmd: "system_pause",
      text: "System Pause",
    },
    {
      name: "CycleStop",
      color: "light-gray",
      cmd: null,
      text: "Cycle Stop",
    },
    {
      name: "SystemStop",
      color: "red",
      cmd: "system_stop",
      text: "System Stop",
    },
  ],
};

var InductionRollerMenu = {
  name: "InductionRollerMenu",
  buttons: [
    {
      name: "InductionRollerConveyorRun",
      color: "green",
      cmd: "induction_roller_on",
      text: "Conveyor Run",
    },
    {
      name: "InductionRollerConveyorStop",
      color: "red",
      cmd: "induction_roller_off",
      text: "Conveyor Stop",
    },
    {
      name: "InductionRollerSpeedOffset",
      color: "gray",
      cmd: null,
      text: "Speed Offset",
    },
    {
      name: "InductionRollerConveyorJog",
      color: "light-gray",
      cmd: "induction_roller_jog",
      text: "Conveyor Jog",
    },
  ],
};
var InductionConveyorMenu = {
  name: "InductionConveyorMenu",
  buttons: [
    {
      name: "InductionConveyorConveyorRun",
      color: "green",
      cmd: "induction_conveyor_on",
      text: "Conveyor Run",
    },
    {
      name: "InductionConveyorConveyorStop",
      color: "red",
      cmd: "induction_conveyor_off",
      text: "Conveyor Stop",
    },
    {
      name: "InductionConveyorSpeedOffset",
      color: "gray",
      cmd: null,
      text: "Speed Offset",
    },
    {
      name: "InductionConveyorConveyorJog",
      color: "light-gray",
      cmd: "induction_conveyor_jog",
      text: "Conveyor Jog",
    },
  ],
};

var VerticalSorterMenu = {
  name: "InductionVerticalSorterMenu",
  buttons: [
    {
      name: "VerticalSorterConveyorRun",
      color: "green",
      cmd: "vertical_conveyor_on",
      text: "Conveyor Run",
    },
    {
      name: "VerticalSorterConveyorStop",
      color: "red",
      cmd: "vertical_conveyor_off",
      text: "Conveyor Stop",
    },
    {
      name: "VerticalSorterConveyorJog",
      color: "light-gray",
      cmd: "vertical_conveyor_jog",
      text: "Conveyor Jog",
    },
    {
      name: "VerticalSorterConveyorRaiseCylinder",
      color: "blue",
      cmd: "vertical_conveyor_raise",
      text: "Raise Cyclinder",
    },
    {
      name: "VerticalSorterConveyorCylinderLowered",
      color: "blue",
      cmd: "vertical_conveyor_lower",
      text: "Lower Cyclinder",
    },
  ],
};

var RecirculationConveyorMenu = {
  name: "RecirculationConveyorMenu",
  buttons: [
    {
      name: "RecirculationConveyorRun",
      color: "green",
      cmd: "rework_conveyor_on",
      text: "Conveyor Run",
    },
    {
      name: "RecirculationConveyorStop",
      color: "red",
      cmd: "rework_conveyor_off",
      text: "Conveyor Stop",
    },
    {
      name: "RecirculationConveyorJog",
      color: "light-gray",
      cmd: "rework_conveyor_jog",
      text: "Conveyor Jog",
    },
  ],
};

var DistributionConveyorMenu = {
  name: "DistributionConveyorMenu",
  buttons: [
    {
      name: "DistributionConveyorRun",
      color: "green",
      cmd: "distribution_conveyor_on",
      text: "Conveyor Run",
    },
    {
      name: "DistributionConveyorStop",
      color: "red",
      cmd: "distribution_conveyor_off",
      text: "Conveyor Stop",
    },
    {
      name: "DistributionConveyorSpeedSet",
      color: "gray",
      cmd: null,
      text: "Speed FPM",
    },
    {
      name: "DistributionConveyorReverseJog",
      color: "dark-green",
      cmd: "distribution_conveyor_rjog",
      text: "Reverse Jog",
    },
    {
      name: "DistributionConveyorForwardJog",
      color: "dark-green",
      cmd: "distribution_conveyor_jog",
      text: "Forward Jog",
    },
    {
      name: "DistributionConveyorResetVFD",
      color: "gray",
      cmd: null,
      text: "Reset VFD",
    },
  ],
};
