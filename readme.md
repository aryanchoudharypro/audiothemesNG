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

## Creating and Editing Audio Themes

You can create your own audio themes or edit existing ones using the Audio Themes Studio.

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