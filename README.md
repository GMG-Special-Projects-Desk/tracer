# tracer

Tracer is a slack bot that scrapes Pacer for new cases of people and companies we are monitoring.

Tracer runs every few hours and whenever it kinds new cases it posts them to the `_k_tracer` channel.\

<img src="https://github.com/GMG-Special-Projects-Desk/tracer/blob/master/tracer.png?raw=true" width="256">

Commands 
--- 
You can also query tracer using its slash command from slack. There are three commands you can use

`/tracer list`

This command shows you all the parties tracer is currently tracking along with the number of cases we have for them.

`/tracer add <name>` 

Allows you to add a new party to tracers list. 
Note: Please be careful to make sure we are not already following the party you're interested in and that you spell the name correctly.

`/tracer search <name>`

Lists all the cases we have for a particular party with basic info plus a link to the Pacer url for the case. 
Note: You will need pacer credentials to see the actual case information.





