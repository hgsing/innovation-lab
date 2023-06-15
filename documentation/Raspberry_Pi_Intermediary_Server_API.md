Connect to 192.168.2.5:1233 via TCP/IP

## Commands: 
-tag read \<tag>
     Description: Returns the value of the tag as a float, or an error code if there was an error processing the command
     Is Simulink Formatted: Yes
     Examples: 
tag read InductionRoller1_PEC
-tag write (repeating: \<tag> \<val>)
     Description: Writes values to the specified tags. If there is an error writing a value, execution will stop early and the error will be returned.
      Returns STATUS_WRITE_OKAY if all writes have no error.
     Is Simulink Formatted: Yes
     Examples:
tag write InductionRoller1_ManRunPB 1
tag write InductionRoller1_ManRunPB 1 InductionRoller1_ManStopPB 0
-tag all
    Description: Will give contextual information about each tag like the type of data it contains. Does NOT give the actual values of the tags. Returns json.
    Is Simulink Formatted: No
    Is Large Formatted: Yes
    Examples:
tag all

-tag read-all
    Description: Will return a json object mapping the name of each tag to its value.
    Is Simulink Formatted: No
    Is Large Formatted: Yes
    Examples:
tag read-all


## What is simulink formatting?
In a simulink formatted command, the first byte of data will always indicate the number of bytes of the remaining data. Logically, this means that data is capped at 255 bytes. To use these commands outside of simulink just ignore the first byte of each response.

Error codes are ALWAYS simulink formatted.


## What is large formatting?
Commands that are large formatted send a lot of data back. So much so that the data will be split into chunks instead of all being sent at once. The data is sent back as a string, with the termination integer 191 (not a valid ascii character). Clients should receive data in a loop until they reach this character.

## Where do I get tags from?
Follow the guide in the “Amatrol Skill Boss Logistics troubleshooting” to load up the .mer file in FactoryTalk View studio
If you are connected to the machine (If not, follow the steps in the troubleshooting doc):
Go to the Explorer pane on the left and click on HMI Tags -> Tags in the pane.
In the GUI that pops up, select ‘Analog’ as the ‘Type’. Then, by ‘Address’, click the 3 dots. Go under ME190215_PLC > Online to view all tags.
Alternatively, go to Graphics -> Displays. Click on the display relevant to the tags you want.
Clicking on a button, then going to connections -> Tag / in the bottom right will show the tag affected when you click the button and also the tag read for the indicator
Click on a text field to see the text with embedded tags. 

For example:
  CONVEYOR SPEED
/*N:2 {[ME190215_PLC]InductionRollerSpeed} NOFILL DP:0*/ FPM
Alternatively, go to 95-MSB 3 Skill Boss Logistics Maintenance and Operation Manual pages 107-109. Tags are listed there but the list is missing a lot of relevant information.

## Status Codes
####	STATUS_UNKNOWN_COMMAND (-27): 
	This error is given when the command parser does not find a valid command matching the syntax provided.
	Examples: 
		ftag read InductionRoller1_PEC
		echo ‘hello’
		random nonsense command
#### STATUS_INVALID_COMMAND_PARAMETERS (-28): 
	This error is given when a command has too many parameters or is missing parameters:
	Examples:
		tag read
		tag read InductionRoller1_PEC 1
		tag write InductionRoller1_PEC 1 32 oranges
#### STATUS_TAG_DOES_NOT_EXIST (-29):
	This error is given when the provided tag does not exist on the Skill Boss Logistics
	Examples: 
		tag read oranges
#### STATUS_TAG_VALUE_CAST_FAILED (-30):
	This error is given when the return value of the tag cannot be casted to a float
	Examples:
		A tag that is not of numeric or boolean type is read
#### STATUS_ERROR_UNKNOWN (-31):
	This error is given when the PLC gives an error that’s not of type ‘Tag doesn’t exist’. The full error will be logged in the console for the server and it can be debugged there.
#### STATUS_PLC_NOT_CONNECTED (-32):
	This error is given when the socket connection to the PLC was never established when the server started. The server may also crash in this case.
#### STATUS_READ_RETURNED_LIST (-33):
	This error should never occur. It is given when a tag read or write returns a list of values.
#### STATUS_WRITE_OKAY (99):
	This status code means all writes successfully occurred!