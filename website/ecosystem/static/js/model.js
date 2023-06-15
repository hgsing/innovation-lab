/*
 * Function definitons for manual_control.html script tag
 */

// Hide options and switch to the menu for a given section name
function SwitchMenu(menu) {
  // Hide all other menus
  $(".controls").children().removeClass("active");

  if (menu === "#Main_Menu") {
    $("#ReturnButton").addClass("hidden");
  } else {
    $("#ReturnButton").removeClass("hidden");
  }

  // Display the div for the selected menu
  $(menu).addClass("active");

  // Remove outlines from svg sections
  for (let section of model.getElementsByTagName("path")) {
    if (
      section.hasAttribute("stroke-width") &&
      section.getAttribute("stroke-width") !== "0.9"
    ) {
      section.setAttribute("stroke-width", "1");
      section.setAttribute("stroke", "black");
    }
  }

  document.getElementById("currentmachine").textContent = menu
    .replaceAll("_", " ")
    .substring(1);
}

function AddOutline(element) {
  const belt = element.querySelector("path.belt");
  belt.setAttribute("stroke-width", "4");
  belt.setAttribute("stroke", "#111111");
  belt.setAttribute("stroke-alignment", "inner");
}

// Change SVG sensor colors when the tag value from the PLC changes (a package is detected)
function recolorSensors(tags) {
  const sensor_tags = [
    "InductionRoller1_PEC", // Induction roller
    "DetectAfterScanner_PEC", // Induction left
    "DetectBeforeScanner_PEC", // Induction right
    "EndofSorterDetect_PEC", // Vertical Sorter
    "EndofReworkDetect", // Recirculation Sensor
    "Sorter1_PkgDetect", // First tray in line
    "Sorter2_PkgDetect", // Second
    "Sorter3_PkgDetect", // Third
    "DistributionConv_PkgRecvdFromSorter", // Distribution conveyor
  ];

  for (const id of sensor_tags) {
    let tag = tags.find((el) => el.name === id);
    if (!!tag) {
      const sensor = model.getElementById(id);

      let detected = tag.value === "True" && tag.value !== "Unknown";

      if (id == "EndofReworkDetect") {
        detected = !detected;
      }

      if (detected) {
        sensor.setAttribute("fill", "red");
      } else {
        sensor.setAttribute("fill", "lime");
      }
    }
  }
}

// Send a POST request to Django views.py /command/<string> route
function SendCMD(command) {
  console.log("cmd", command);
  $.ajax({
    type: "POST",
    url: "/command/" + command,
  });
}

function Send_CMD_Value(command, value) {
  $.ajax({
    type: "POST",
    url: "/command/" + command + "/" + value,
  });
}

function toggleVacuum(element) {
  let el = $(element);

  if (element.classList[0] == "red") {
    el.removeClass("red");
    el.addClass("green");
    el.text("Vacuum On");
    SendCMD("diverter_3_off");
  } else if (element.classList[0] == "green") {
    el.removeClass("green");
    el.addClass("red");
    el.text("Vacuum Off");
    SendCMD("diverter_3_on");
  }
}

function toggleJam(element) {
  let el = $(element);
}

// Line Speed stuff
const speedModal = document.getElementById("speedModal");
const selection = speedModal.querySelector("input");
const confirmBtn = speedModal.querySelector("#confirmBtn");

selection.addEventListener("change", (e) => {
  confirmBtn.value = selection.value;
});

speedModal.addEventListener("close", (e) => {
  const btn = $(document.activeElement)[0];
  let res = speedModal.returnValue === "" ? 50.0 : speedModal.returnValue;

  Send_CMD_Value(btn.dataset.cmd, res);
});

confirmBtn.addEventListener("click", (event) => {
  event.preventDefault();
  speedModal.close(selection.value);
});
