# coding: utf-8

# Copyright (c) 2014-2019 Musharraf Omer
# This file is covered by the GNU General Public License.

"""
  Audio Themes Add-on
  ~~~~~~~~~~~~~~~~~~~~~~
  This add-on creates a virtual audio display that plays sounds when focusing or navigating objects, the audio
  will be played in a location that corresponds to the object's location in the visual display. It also enables the user to
  activate, install, remove, edit, create, and distribute audio theme packages.

  Started as an indipendant project, this addon evolved to be an enhanced version of the 'Unspoken' addon
  by Austin Hicks (camlorn38@gmail.com).

  The development of this addon is happening on GitHub <http://github.com/mush42/Audio-Themes-NVDA-Add-on>
  Crafted by Musharraf Omer <ibnomer2011@hotmail.com> using code published by  others from the NVDA community.
"""

from contextlib import suppress
import wx
import globalPluginHandler
import appModuleHandler
import scriptHandler
import NVDAObjects
import gui
import speech
import controlTypes
import globalCommands
import eventHandler
import inputCore
import winInputHook
import winUser
import textInfos
import treeInterceptorHandler
from .handler import AudioThemesHandler, SpecialProps
from .settings import AudioThemesSettingsPanel
from .studio import AudioThemesStudioStartupDialog

import api

import addonHandler
addonHandler.initTranslation()


EDIT_ROLES = {
    controlTypes.Role.EDITABLETEXT,
    controlTypes.Role.RICHEDIT,
    controlTypes.Role.PASSWORDEDIT,
    controlTypes.Role.DOCUMENT,
    controlTypes.Role.TERMINAL,
    controlTypes.Role.DATEEDITOR,
    controlTypes.Role.HOTKEYFIELD,
    controlTypes.Role.IPADDRESS,
}

BUTTON_ROLES = {
    controlTypes.Role.BUTTON,
    controlTypes.Role.DROPDOWNBUTTON,
    controlTypes.Role.MENUBUTTON,
    controlTypes.Role.SPLITBUTTON,
    controlTypes.Role.DROPDOWNBUTTONGRID,
    controlTypes.Role.TREEVIEWBUTTON,
}

ENTER_ACTIVATION_ROLES = {
    controlTypes.Role.BUTTON,
    controlTypes.Role.DROPDOWNBUTTON,
    controlTypes.Role.MENUBUTTON,
    controlTypes.Role.SPLITBUTTON,
    controlTypes.Role.DROPDOWNBUTTONGRID,
    controlTypes.Role.TREEVIEWBUTTON,
    controlTypes.Role.LISTITEM,
    controlTypes.Role.DESKTOPICON,
    controlTypes.Role.ICON,
    controlTypes.Role.TREEVIEWITEM,
    controlTypes.Role.MENUITEM,
    controlTypes.Role.LINK,
    controlTypes.Role.TAB,
}

TOGGLE_ROLES = {
    controlTypes.Role.CHECKBOX,
    controlTypes.Role.TOGGLEBUTTON,
    controlTypes.Role.CHECKMENUITEM,
    controlTypes.Role.RADIOBUTTON,
    controlTypes.Role.RADIOMENUITEM,
}
if hasattr(controlTypes.Role, "SWITCH"):
    TOGGLE_ROLES.add(controlTypes.Role.SWITCH)


class BrowseModeProxyTarget:
    def __init__(self, root, location=None, role=None, states=None):
        self.role = role or controlTypes.Role.LINK
        self.states = states or {controlTypes.State.LINKED}
        self.windowHandle = getattr(root, "windowHandle", 0)
        self.location = location


def _is_edit_object(obj):
    if not obj:
        return False
    role = getattr(obj, "role", None)
    states = getattr(obj, "states", set())
    editable_state = getattr(controlTypes.State, "EDITABLE", None)
    readonly_state = getattr(controlTypes.State, "READONLY", None)
    is_readonly = bool(readonly_state and readonly_state in states)

    # In browse mode virtual buffers, the document itself has Role.DOCUMENT,
    # but it is not an interactive text-editing input box unless it has EDITABLE without READONLY
    ti = getattr(obj, "treeInterceptor", None)
    is_browse_mode_buffer = bool(ti and getattr(ti, "isReady", False) and not getattr(ti, "passThrough", False))

    if is_browse_mode_buffer:
        if role in (controlTypes.Role.EDITABLETEXT, controlTypes.Role.PASSWORDEDIT):
            return not is_readonly
        if editable_state and editable_state in states:
            return not is_readonly
        return False

    if role in EDIT_ROLES:
        if is_readonly:
            return False
        return True

    if editable_state and editable_state in states and not is_readonly:
        return True

    return False


def _is_toggle_object(obj):
    if not obj:
        return False
    role = getattr(obj, "role", None)
    if role in TOGGLE_ROLES:
        return True
    states = getattr(obj, "states", set())
    checkable_state = getattr(controlTypes.State, "CHECKABLE", None)
    if checkable_state and checkable_state in states:
        return True
    return False


def _find_activatable_target(start_obj, is_space=False, is_enter=False, is_mouse=False):
    """
    Checks start_obj and its immediate ancestors (up to 4 levels)
    to find an activatable object (e.g. link, button, listitem, etc.).
    Returns the target object to play sound on, or None.
    """
    if not start_obj:
        return None

    # Never play click sounds while typing inside any text edit control
    if _is_edit_object(start_obj):
        return None

    target = start_obj
    for _ in range(4):
        if not target:
            break

        role = getattr(target, "role", None)
        states = getattr(target, "states", set())

        # If we hit an edit control in the hierarchy, stop
        if _is_edit_object(target):
            return None

        # Link check (Role.LINK or State.LINKED)
        linked_state = getattr(controlTypes.State, "LINKED", None)
        is_link = (role == controlTypes.Role.LINK) or (linked_state and linked_state in states)

        if is_link:
            return target

        if is_space:
            if _is_toggle_object(target):
                # Toggle sound is handled by event_stateChange
                return None
            if role in BUTTON_ROLES:
                return target

        if is_enter:
            if role in ENTER_ACTIVATION_ROLES:
                return target

        if is_mouse:
            if role in ENTER_ACTIVATION_ROLES or _is_toggle_object(target):
                return target
            clickable_state = getattr(controlTypes.State, "CLICKABLE", None)
            if clickable_state and clickable_state in states:
                return target

        target = getattr(target, "parent", None)

    return None


def _get_browse_mode_target(focus, is_space=False, is_enter=False):
    """
    If the current focus is in Browse Mode (virtual buffer), inspect the virtual buffer
    caret position and controls to find if a link, button, or activatable element is focused.
    """
    if not focus:
        return None
    ti = getattr(focus, "treeInterceptor", None)
    if not ti:
        with suppress(Exception):
            ti = treeInterceptorHandler.getTreeInterceptor(focus)
    if not ti or not getattr(ti, "isReady", False) or getattr(ti, "passThrough", False):
        return None

    # 1. Inspect direct NVDAObjects provided by the virtual buffer at the caret
    candidate_objs = []
    for attr in ("currentFocusableNVDAObject", "currentNVDAObject"):
        with suppress(Exception):
            o = getattr(ti, attr, None)
            if o and o != getattr(ti, "rootNVDAObject", None):
                candidate_objs.append(o)

    with suppress(Exception):
        info = ti.makeTextInfo(textInfos.POSITION_CARET)
        if info:
            for attr in ("focusableNVDAObjectAtStart", "NVDAObjectAtStart"):
                o = getattr(info, attr, None)
                if o and o != getattr(ti, "rootNVDAObject", None):
                    candidate_objs.append(o)

    with suppress(Exception):
        nav = api.getNavigatorObject()
        if nav and getattr(nav, "treeInterceptor", None) == ti and nav != getattr(ti, "rootNVDAObject", None):
            candidate_objs.append(nav)

    for obj in candidate_objs:
        target = _find_activatable_target(obj, is_space=is_space, is_enter=is_enter)
        if target:
            return target

    # 2. Inspect virtual buffer fields at caret (handles virtual buffer nodes where NVDAObject is synthetic/text)
    try:
        info = ti.makeTextInfo(textInfos.POSITION_CARET)
        if info:
            info_char = info.copy()
            info_char.expand(textInfos.UNIT_CHARACTER)
            for item in reversed(info_char.getTextWithFields()):
                if getattr(item, "command", None) == "controlStart":
                    field = getattr(item, "field", {})
                    f_role = field.get("role")
                    f_states = field.get("states", set()) or set()
                    is_link = (
                        f_role in (controlTypes.Role.LINK, "link", 19, "19")
                        or str(f_role).lower() in ("link", "role.link")
                        or (hasattr(controlTypes, "State") and getattr(controlTypes.State, "LINKED", None) in f_states)
                    )
                    is_btn = (
                        f_role in (controlTypes.Role.BUTTON, "button", 9, "9")
                        or str(f_role).lower() in ("button", "role.button")
                    )
                    if is_link or is_btn:
                        loc = getattr(info, "location", None) or getattr(focus, "location", None)
                        role = controlTypes.Role.LINK if is_link else controlTypes.Role.BUTTON
                        states = {controlTypes.State.LINKED} if is_link else set()
                        return BrowseModeProxyTarget(getattr(ti, "rootNVDAObject", focus), location=loc, role=role, states=states)
    except Exception:
        pass

    return None


def _is_checked(obj):
    states = getattr(obj, "states", set())
    checked_states = []
    for s_name in ("CHECKED", "PRESSED", "ON"):
        s_val = getattr(controlTypes.State, s_name, None)
        if s_val is not None:
            checked_states.append(s_val)
    return any(st in states for st in checked_states)


def _get_object_key(obj):
    try:
        return (obj.windowHandle, getattr(obj, "IAccessibleChildID", None), obj.role, obj.name)
    except Exception:
        return id(obj)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    browser_apps = ["firefox", "iexplore", "chrome", "opera", "edge"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = AudioThemesHandler()
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
            AudioThemesSettingsPanel
        )
        self._previous_mouse_object = None
        self._last_navigator_object = None
        self._last_checked_states = {}
        # Add the menu item for the audio themes studio
        self.studioMenuItem = gui.mainFrame.sysTrayIcon.menu.Insert(
            2,
            wx.ID_ANY,
            # Translators: label for the audio themes studio menu item
            _("&Audio Themes Studio"),
        )
        gui.mainFrame.sysTrayIcon.Bind(
            wx.EVT_MENU, self.on_studio_item_clicked, self.studioMenuItem
        )
        self._navigation_timer = wx.Timer()
        self._navigation_timer.Bind(wx.EVT_TIMER, self._onNavigationTimer)
        self._navigation_timer.Start(100)  # Check every 100ms

        # Register gesture hook for button click sounds
        with suppress(Exception):
            inputCore.decide_executeGesture.register(self._on_decide_execute_gesture)

        # Register mouse hook for mouse clicks on buttons
        self._orig_mouseCallback = getattr(winInputHook, "mouseCallback", None)
        with suppress(Exception):
            winInputHook.mouseCallback = self._on_mouse_event

    def terminate(self):
        with suppress(Exception):
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
                AudioThemesSettingsPanel
            )
            gui.mainFrame.sysTrayIcon.menu.RemoveItem(self.studioMenuItem)
            self.handler.close()
            self._navigation_timer.Stop()
            inputCore.decide_executeGesture.unregister(self._on_decide_execute_gesture)
            if hasattr(self, "_orig_mouseCallback"):
                winInputHook.mouseCallback = self._orig_mouseCallback

    def _on_decide_execute_gesture(self, gesture):
        try:
            if not self.handler.enabled or not getattr(self.handler, "play_click_sounds", True):
                return True

            # Ignore when input help is active or a gesture captor is running
            if getattr(inputCore.manager, "isInputHelpActive", False):
                return True
            if getattr(inputCore.manager, "_captureFunc", None) is not None:
                return True

            # Ignore if current focus is in sleep mode
            focus = api.getFocusObject()
            if not focus or getattr(focus, "sleepMode", False):
                return True

            is_space = False
            is_enter = False
            identifiers = getattr(gesture, "identifiers", [])
            for ident in identifiers:
                lower_ident = ident.lower()
                key_part = lower_ident.split(":", 1)[-1] if ":" in lower_ident else lower_ident
                # Ignore if modifier keys are pressed (e.g. nvda+enter, ctrl+space)
                if "+" in key_part:
                    continue
                if key_part == "space":
                    is_space = True
                    break
                elif key_part in ("enter", "numpadenter"):
                    is_enter = True
                    break

            if not (is_space or is_enter) and hasattr(gesture, "vkCode"):
                mods = getattr(gesture, "modifierNames", None) or getattr(gesture, "modifiers", None)
                if not mods:
                    if gesture.vkCode == winUser.VK_SPACE:
                        is_space = True
                    elif gesture.vkCode == winUser.VK_RETURN:
                        is_enter = True

            script = getattr(gesture, "script", None)
            if not script:
                with suppress(Exception):
                    import scriptHandler
                    script = scriptHandler.findScript(gesture)

            script_name = getattr(script, "__name__", "")
            if script_name == "script_activatePosition":
                ti = getattr(script, "__self__", None)
                target = getattr(ti, "currentNVDAObject", None) or getattr(ti, "currentFocusableNVDAObject", None) or getattr(ti, "rootNVDAObject", None) or focus
                self.handler.play(target, SpecialProps.click)
                return True

            if is_space or is_enter:
                target = _get_browse_mode_target(focus, is_space=is_space, is_enter=is_enter)
                if not target:
                    target = _find_activatable_target(focus, is_space=is_space, is_enter=is_enter)
                if target:
                    self.handler.play(target, SpecialProps.click)
        except Exception:
            pass
        return True

    def _on_mouse_event(self, msg, x, y, injected):
        try:
            if self.handler.enabled and getattr(self.handler, "play_click_sounds", True):
                if not getattr(inputCore.manager, "isInputHelpActive", False) and getattr(inputCore.manager, "_captureFunc", None) is None:
                    if msg in (winUser.WM_LBUTTONDOWN, winUser.WM_LBUTTONDBLCLK):
                        desktop = api.getDesktopObject()
                        if desktop:
                            obj = desktop.objectFromPoint(x, y)
                            target = _find_activatable_target(obj, is_mouse=True)
                            if target:
                                self.handler.play(target, SpecialProps.click)
        except Exception:
            pass
        if self._orig_mouseCallback:
            return self._orig_mouseCallback(msg, x, y, injected)
        return True

    def _onNavigationTimer(self, event):
        try:
            current_nav = api.getNavigatorObject()
            # Check if treeInterceptor is not None, then check its passThrough property.
            if current_nav.treeInterceptor and not current_nav.treeInterceptor.passThrough:
                if current_nav and current_nav != self._last_navigator_object:
                    self._last_navigator_object = current_nav
                    self.playObject(current_nav)
        except:
            pass

    def on_studio_item_clicked(self, event):
        # Translators: title for the audio themes studio dialog
        with AudioThemesStudioStartupDialog(self, _("Audio Themes Studio")) as dlg:
            dlg.ShowModal()

    def script_speakObject(self, gesture):
        if scriptHandler.getLastScriptRepeatCount() == 0:
            self.playObject(NVDAObjects.api.getFocusObject())
        globalCommands.commands.script_reportCurrentFocus(gesture)

    script_speakObject.__doc__ = (
        globalCommands.GlobalCommands.script_reportCurrentFocus.__doc__
    )

    def event_gainFocus(self, obj, nextHandler):
        if _is_toggle_object(obj):
            self._last_checked_states[_get_object_key(obj)] = _is_checked(obj)
        # Prevent firing when browse mode is active.
        # Check if treeInterceptor is not None, then check its passThrough property.
        if not (obj.treeInterceptor and not obj.treeInterceptor.passThrough):
            self.playObject(obj)
        nextHandler()

    def event_stateChange(self, obj, nextHandler):
        if self.handler.enabled and getattr(self.handler, "play_toggle_sounds", True):
            if _is_toggle_object(obj):
                is_on = _is_checked(obj)
                key = _get_object_key(obj)
                prev_on = self._last_checked_states.get(key)
                if prev_on is None or prev_on != is_on:
                    self._last_checked_states[key] = is_on
                    if is_on:
                        self.handler.play(obj, SpecialProps.toggle_on)
                    else:
                        self.handler.play(obj, SpecialProps.toggle_off)
        nextHandler()

    def event_becomeNavigatorObject(self, obj, nextHandler, isFocus=False):
        # Prevent firing when browse mode is active.
        # Check if treeInterceptor is not None, then check its passThrough property.
        if not (obj.treeInterceptor and not obj.treeInterceptor.passThrough):
            self.playObject(obj)
        nextHandler()

    def event_mouseMove(self, obj, nextHandler, x, y):
        if obj is not self._previous_mouse_object:
            self._previous_mouse_object = obj
            self.playObject(obj)
        nextHandler()

    def event_show(self, obj, nextHandler):
        if obj.role == controlTypes.ROLE_HELPBALLOON:
            obj.snd = SpecialProps.notify
            self.playObject(obj)
        nextHandler()

    def event_documentLoadComplete(self, obj, nextHandler):
        if appModuleHandler.getAppNameFromProcessID(obj.processID) in self.browser_apps:
            self.playObject(obj)
        nextHandler()

    def playObject(self, obj):
        order = self.getOrder(obj)
        if getattr(obj, "snd", None) is None:
            if 16384 in obj.states:
                obj.snd = SpecialProps.protected
            elif order:
                obj.snd = order
            else:
                obj.snd = obj.role
        self.handler.play(obj, obj.snd)

    def getOrder(self, obj, parrole=14, chrole=15):
        if obj.parent and obj.parent.role != parrole:
            return None
        if (obj.previous is None) or (obj.previous.role != chrole):
            return SpecialProps.first
        elif (obj.next is None) or (obj.next.role != chrole):
            return SpecialProps.last

    __gestures = {
        "kb:nvda+tab": "speakObject",
    }