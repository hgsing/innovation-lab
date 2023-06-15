# Innovation Research Lab - Ecosystem Monitor
Project contains a website written using Django, JQuery, and vanilla JavaScript/HTML/CSS to display data from and communicate with various devices in the Innovation Research Lab.

# Folder Structure
```bash
├───docs 		# Project wide documentation, also holds related documentation for FaultPro and FactoryTalk Studio
│   └───images
├───PLC 		# Python files used to communicate with the Skill Boss Logistics device
└───website 		# All files related to the Django website
    ├───ecosystem 	# Main 'application' of the website
    │   ├───static
    │   │   ├───css
    │   │   ├───img
    │   │   └───js
    │   └───templates 	# Contains HTML and SVG files used in the website
	└───labproject 	# Django project settings
```

# Usage
To get started, install dependencies using `pip -r requirements.txt` then cd into the website folder. Start the server either by running `python manage.py runserver` or if using VS Code use the task `Start website` (Open command pallete -> Run task -> Start website).

The website opens at `127.0.0.1:8000` but will not be functional unless you start the socket server. CD into the PLC folder and run `python pi-socket-server.py` or use the VS Code build task `Start PI Server`. For convienicce you can run both tasks in parallel using the default build task `Run together` which by default is bound to the shortcut `Ctrl+Shift+B`.

# Website
The website has three main sections accessable from the top nav bar- Home, Control Panel, and Manual Control.

- ### Home 
	Displays a grid with all the lab's devices. Each device which has an active connection displays white text and is a clickable link to a page with a table of data.

- ### Control Panel 
  	A collection of buttons that change some site settings. Importantly, you can click Reconnect Devices to reset all devices if any issues occur.

- ### Manual Control
  	Used to control the Skill Boss Logisitics machine. Displays a large SVG image with clickable sections and a grid of buttons to control the device.

# Contributors
Daniel Delannes-molka	<ddelanne@gmu.edu>

Hayden Singleton	<hsinglet@gmu.edu>

Previous work - Aaron Rahman, Brian Nguyen
