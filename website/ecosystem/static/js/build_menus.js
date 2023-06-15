function createButton(options, listener = undefined) {
  let btn = document.createElement("button");
  btn.id = options.name;
  btn.type = "button";
  btn.className = options.color;
  btn.textContent = options.text;
  if (options.cmd) {
    btn.addEventListener("click", () => SendCMD(options.cmd));
  }
  if (listener) {
    btn.addEventListener("click", listener);
  }

  return btn;
}

const controls = document.getElementsByName("controls")[0];

function buildMenu(menu) {
  const menuDiv = controls.appendChild(document.createElement("div"));
  if (menu.name !== "MainMenu") {
    menuDiv.appendChild(ToMainMenu);
  }
  menuDiv.id = menu.name;
  for (let item of menu.buttons) {
    menuDiv.appendChild(createButton(item));
  }
}

function clearMenus() {
  while (controls.hasChildNodes()) {
    controls.removeChild(controls.firstChild);
  }
}

SwitchMenu("Main");

// Create button to add to all sub-menus
const ToMainMenu = createButton(
  {
    name: "ToMainMenu",
    color: "dark-blue",
    text: "Main Menu",
  },
  () => SwitchMenu("Main")
);

// Set up last updated display

let initial_connection = "{{ active_connection }}" === "True";
let last_updated = $("#updated");

if (initial_connection) {
  let time = "Last updated: " + new Date().toLocaleString("en");
  last_updated.text(time);
} else {
  last_updated.text("No connection to PLC");
}

// Update page (color/update time) on interval

$(document).ready(() =>
  setInterval(() => {
    $.ajax({ method: "GET", url: "/raw/skill-boss-logistics" }).done((data) => {
      if (data.connection) {
        $("#updated").text("Last updated: " + new Date().toLocaleString("en"));
        last_updated.textContent =
          "Last updated: " +
          new Date().toLocaleString("en", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          });

        let tags = Object.values(data.tags);

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
      } else {
        $("button").prop("style", "cursor: disabled;");
      }
    });
  }, 250)
);

// Add event listeners to SVG sections

const model = document.getElementById("2Dmodel");
const roller = model.getElementById("InductionRoller");
roller.addEventListener("click", () => {
  SwitchMenu("Induction Roller");
});

model
  .getElementById("InductionConveyor")
  .addEventListener("click", function () {
    SwitchMenu("Induction Conveyor");
  });

model
  .getElementById("VerticalSorterConveyor")
  .addEventListener("click", function () {
    SwitchMenu("Vertical Sorter Conveyor");
  });

model
  .getElementById("RecirculationConveyor")
  .addEventListener("click", function () {
    SwitchMenu("Recirculation Conveyor");
  });

model
  .getElementById("DistributionConveyor")
  .addEventListener("click", function () {
    SwitchMenu("Distribution Conveyor");
  });

// Hide options and switch to the menu for a given section name
function SwitchMenu(name) {
  const sections = [
    "#InductionRoller",
    "#InductionConveyor",
    "#VerticalSorterConveyor",
    "#RecirculationConveyor",
    "#DistributionConveyor",
  ];

  // Hide outlines on other areas
  for (let section of sections) {
    let rect = $(section).children(".belt");
    if (rect) {
      rect[0].setAttribute("stroke-width", "1");
    }
  }

  clearMenus();

  switch (name) {
    case "Induction Roller":
      buildMenu(InductionRollerMenu);
      break;
    case "Induction Conveyor":
      buildMenu(InductionConveyorMenu);
      break;
    case "Vertical Sorter Conveyor":
      buildMenu(VerticalSorterMenu);
      break;
    case "Recirculation Conveyor":
      buildMenu(RecirculationConveyorMenu);
      break;
    case "Distribution Conveyor":
      buildMenu(DistributionConveyorMenu);
      break;
    default:
      buildMenu(MainMenu);
  }

  if (name === "Main") {
    $("#currentmachine").text("Main Menu");
  } else {
    $("#currentmachine").html(name);

    // Outline this area
    $("#" + name.replaceAll(" ", ""))
      .children(".belt")[0]
      .setAttribute("stroke-width", "4");
  }
}

// Send a POST request to Django views.py /command/<string> route
function SendCMD(command) {
  console.log('Sending "' + command + '"');
  $.ajax({
    type: "POST",
    url: "/command/" + command,
  });
}
