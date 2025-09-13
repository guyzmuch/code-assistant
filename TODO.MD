sqLite database to list the plugin, set the one that are activatet or not
in the database, we save a custom name, a selected option for the plugin, if the plugin is activated or not, if the plugin is new or not, and the keyboard shortcut to launch the plugin
the app setup should take the database into account by activating it or not, and setting the plugin with the correct option and shortcut. also, it should add any new plugin to the database
there can be multiple time the same plugin in the application, for example with different options
we can create custom action buttons that pipes different plugins together (this should be set in the database)
history of results and easy acces to it
on the interface, there is a windows to list the plugin, select the one to activate, choose there options, and create custom ones
also, on the interface, we can set up keyboard shortcut for each plugin to launch either the normal function, or the one from clipboard https://www.pythontutorial.net/tkinter/tkinter-event-binding/#the-levels-of-binding
add the posibilities to have plugins child of other plugins, with for example specific options already set
I want my plugin to possibly have a test value to be set up in the interface, like the options, but here a text box. that could be useful for the line merge character, or ???
a special plugins at the bottom. that could be use to have timers, like to do the pomodoro method within the app
options to keep the windows always on top #root.attributes('-topmost', 1)#

## PLUGINGS IDEA
general converter (like seconds to hours, or celcius to farhenheit) where you can set up the conversion value and a name
functionnality to merge lines into one with configurable characters




## LONG TERM
have keyboard shortcut that can be set to different button
ability to select wich functionnality to show on the interface


## DONE
change the placement of items using grid
buttons to copy the result
button to move the result to the input
plugins should be classes following a certain schematic