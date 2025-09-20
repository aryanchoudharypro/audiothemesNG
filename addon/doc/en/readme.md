# Audio Themes Add-on For NVDA

## Introduction
The Audio Themes add-on creates a virtual audio display that plays sounds when focusing or navigating objects (such as buttons, links etc...) the audio will be played in a location that corresponds to the object's location in the visual display. The add-on also enables you to activate, add, remove, edit, create, and distribute audio theme packages.

## Usage

This add-on enhances your experience with NVDA in the following ways:

1. When focusing or navigating objects, the add-on plays a preassigned audio file from the currently active audio theme.
2. You can activate or remove an existing audio theme. You can also add an audio theme package to your audio themes collection.
3. Through the Audio Themes Studio, you can create a new audio theme for your personal use or for sharing with others. You can also edit an existing audio theme as well.

## Customizing the add-on

The settings for the Audio Themes add-on could be found in NVDA's settings dialog under the name "Audio Themes". You can customize the add-on in the following ways:

* To enable or disable the add-on, use the "Enable Audio Themes" check box.
* To activate an existing audio theme, select an audio theme from the "Select Theme" combobox and press the enter key. To permanently use the selected theme, you need to save your NVDA configurations by activating the "Save Configuration" menu item found in the NVDA's menu.
* To get more information about the selected audio theme, press the "About" button. This will give you a brief summary about the audio theme, such as its name, author, and description.
* To remove an existing audio theme, activate the "Remove" button, a confirmation message will be shown, pressing yes on this message will remove the selected theme.
* To add a new audio theme to your audio themes collection, activate the "Add New..." button, the familiar open file dialog will be shown, browse to your audio theme package, a file with an extension of .atp, and activate the Ok button. If the process is successful, you will find your newly added audio theme among your existing audio themes.
* You can control whether NVDA announces objects roles (such as button, link, checkbox..etc) by checking/unchecking the "Speak roles such as button, edit box, link..etc" check box.
* The announcement of roles during say-all could be enabled or disabled by checking/unchecking the "Speak roles during say-all check box".
* The volume of the played sounds could be adjusted in two ways:

1. You can set the volume of the audio-themes add-on to follow the volume of the currently used speech synthesizer by checking the "Use speech synthesizer volume" check box.
2. If you want to set a custom volume level for audio themes, you need to uncheck the "Use speech synthesizer volume" check box, and then use the "Audio themes volume" slider to set your preferred volume level.


## Audio Themes Studio

The Audio Themes Studio is your one-stop-shop for all things audio themes. Using the studio, you can create a new audio theme and package it for personal use or distribution. You can also use the studio to edit any one of your existing audio themes.

Note that the add-on supports two audio formats, namely: *.ogg and *.wav. Please make sure that your sounds are properly converted to one of these two formats before starting. You can freely mix the two if you need to.

Please make sure that your sounds are short in length. To get the best results, do not use sounds longer than two seconds. 

### Creating and editing audio themes

The interface for creating and editing audio themes is pretty intuitive and self-explanatory, it is the same whether you are creating a new audio theme or editing an existing one. The only difference is that pressing the save button when creating an audio theme will package and save the new theme to a file, and pressing the save button when editing an audio theme will save your changes to the existing audio theme.

#### Creating a new audio theme

To create an audio theme follow these steps:

* From NVDA's menu, activate the "Audio Themes Studio" menu item
* From the Audio Themes Studio, activate the "Create new audio theme" button
* In the "Enter theme information" dialog, type in the theme name, author, and description
* The first thing that faces you in the next dialog is a list of the currently added sounds. When creating a new audio theme, this list will be initially empty.
* To add a new sound, activate the "Add..." button, a dialog containing a list of object's roles would be shown, select the role of the object, and browse to the audio file you want to assign to objects with the selected role, then activate the OK button to add it.
* To change an existing sound, select its corresponding item from the list, activate the "Change" button, and browse to your desired audio file.
* To remove an existing sound, select its corresponding item from the list and activate the "Remove" button. The sound would be removed from the audio theme.
* When done, activate the save button, and browse to the folder to which your audio theme package will be saved. 

#### Editing an existing audio theme

The process of editing an audio theme is almost identical to the process of creating a new audio theme. The only differences are:

* When activating the "Customize existing audio theme" button from the audio themes studio, a dialog will be opened from which you must select one of your existing audio themes for editing.
* When activating the "Save" button in the audio themes editor, the changes would be saved and applied immediately to the selected audio theme.

## Copyright

Copyright (c) 2014-2019 Musharraf Omer<ibnomer2011@hotmail.com>.

Although this add-on was started as an independent project, it has evolved to be an enhanced version of the 'Unspoken' add-on by Austin Hicks (camlorn38@gmail.com) and Bryan Smart (bryansmart@bryansmart.com). The majority of this add-on's development went into creating the tools to manage, edit and create audio theme packages. So a big thank you to these two guys for creating such a wonderful add-on, and open sourcing it so others can build on top of their work.


## A Note on Third-party audio files:
The **Default** audio theme package in this add-on uses sounds from several sources, here is a breakdown for those sources:
- Unspoken 3D Audio: An add-on for NVDA
- TWBlue: A free and open source twitter client
- Mushy TalkBack: An alternative talkback with better sounds.


## License
Licensed under the GNU General Public License. See the file **copying** for more details.
