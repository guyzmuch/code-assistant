we should simplify the class so that wi don't need to call "apply_for_all_lines" everytime. maybe we could use 2 different function in the class, one called for each line, and one called for all, and both can be set, or not.
on top of the description, plugins can have a example part, that will be a list of tuple with input output. the interface can later display this (like separate input/output with arrow or something). But how to deal with plugins having one output for several input, or vice versa??
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
above the result, we should have name of the plugin that generated the result (it should also be showed in the history)

## PLUGINGS IDEA
general converter (like seconds to hours, or celcius to farhenheit) where you can set up the conversion value and a name. this should allow to have formula with variable (because for example celcius = (farhenheit - 32) * 5/9)
functionnality to merge lines into one with configurable characters
do sha manipulation on a list, with option for the type of crypto and also a field to put the signature
conversion between hexa and numbers, and vice versa
we need to be able to export or plugin config, and or pipes of plugins, so we can share them easily (and have backup) (should it be a JSON format saved in a .codeassistantrc?)



## LONG TERM
options to keep the windows always on top #root.attributes('-topmost', 1)#
possibility to have a vertical line up of the interface aka top to bottom
have keyboard shortcut that can be set to different button
ability to select wich functionnality to show on the interface


## DONE
change the placement of items using grid
buttons to copy the result
button to move the result to the input
plugins should be classes following a certain schematic