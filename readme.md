# Audio Themes NVDA Add-on

This add-on provides an immersive audio experience for NVDA screen reader users by playing sounds for various UI events. It allows for the creation, installation, and customization of audio themes, enhancing the auditory feedback from the user interface.

## Features

- **Audio effects :** Plays sounds for UI events such as focusing on controls, navigating lists, and more.
- **3D Audio:** Utilizes Steam Audio to provide 3D positional audio, giving a sense of where controls are on the screen.
- **Reverb:** Adds reverb effects to the audio for a more immersive experience.
- **Customizable Themes:** Allows users to create, install, and switch between different audio themes.
- **Audio Themes Studio:** A built-in tool to create new audio themes or edit existing ones.
- **Configuration:** Provides a settings panel to enable/disable features, adjust volume, and configure 3D audio and reverb settings.

## Installation

1. Download the latest release of the add-on from the [releases page]
2. Open the downloaded `.nvda-addon` file.
3. NVDA will ask you to confirm the installation. Choose "Yes".
4. Restart NVDA to complete the installation.

## How to Use

### Enabling/Disabling Audio Themes

You can enable or disable the audio themes feature in NVDA's settings:

1. Open the NVDA menu (NVDA+N).
2. Go to "Preferences" -> "Settings".
3. In the settings dialog, select the "Audio Themes" category.
4. Check or uncheck the "Enable audio themes" checkbox.

### Selecting and Managing Themes

In the "Audio Themes" settings panel, you can:

- **Select a theme:** Choose from the list of installed audio themes.
- **Add a new theme:** Click the "Add New..." button to install a theme from an `.atp` file.
- **Remove a theme:** Select a theme and click the "Remove" button.
- **About a theme:** Click the "About" button to see information about the selected theme.

### Using the Audio Themes Studio

The Audio Themes Studio allows you to create and edit audio themes. To open the studio:

1. Open the NVDA menu (NVDA+N).
2. Select "Audio Themes Studio".

In the studio, you can:

- **Create a new audio theme:** This will guide you through the process of creating a new theme from scratch.
- **Customize an existing audio theme:** Select this option to modify the sounds of an installed theme. You can change existing sounds, add new ones, or remove sounds from the theme.

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
* When activating the "Save" button in the audio themes editor, the changes would be saved and applied immediately to the selected audio theme. if you want to export, you will find a button to do so in the editer 

### Audio File Requirements

When adding sounds to a theme, make sure they meet the following requirements:

- **Format:** The audio files must be in `.wav` format.
- **Sample Rate:** The recommended sample rate is 44100 Hz.

### Exporting Your Theme

After creating or editing a theme, you can export it as an `.atp` file. This file can be shared with other users or used as a backup. You can find the export option in the editing screen. when you make a theme for the first time, the export dialog will come up as soon as you hit the save button 

## Configuration

The "Audio Themes" settings panel provides several options to customize your experience:

- **Enable audio themes:** Toggles the add-on on or off.
- **Select theme:** Choose the active audio theme.
- **Play sounds in 3D mode:** Enables or disables 3D audio.
- **Speak roles...:** When unchecked, NVDA will not speak the role of a control if a sound is played for it.
- **Speak roles during say all:** When checked, roles will be spoken during a "say all" session.
- **Use speech synthesizer volume:** When checked, the add-on's volume will match the synthesizer's volume.
- **Audio themes volume:** Adjust the volume of the audio themes.
- **Reverb Settings:**
  - **Enable Reverb:** Toggles the reverb effect.
  - **Room Size, Damping, Wet Level, Dry Level, Width:** Adjust the reverb parameters.

## Credits

the first version of this addon was made by Musharraf Omer: ibnomer2011@hotmail.com
huge thanks to all the people who worked on the unspoken addon, that is the base for all the audio themes versions! 
• Bryan Smart: the original work on two versions of the Unspoken addon
• Masonasons: updating the Unspoken addon with the API changes in 2023 and 2024
• Ambro86: maintaining modern Python bindings for synthizer, as well as contributing some code to unspoken
• Tyler Spivey: for sitting down, figuring out steam audio, and creating Python bindings that do what was needed! 
• Samuel Proulx, for releasing the unspokenNG addon.  