# Unspoken user interface feedback for NVDA
# By Bryan Smart (bryansmart@bryansmart.com) and Austin Hicks (camlorn38@gmail.com)
# Updated to use Synthizer by Mason Armstrong (mason@masonasons.me)

import atexit
import os
import os.path
import sys
import time
import threading
import wave
import struct
import globalPluginHandler
import NVDAObjects
import config
import speech
import controlTypes
from speech.sayAll import SayAllHandler
from logHandler import log
import gui
import api
import textInfos
import wx
import nvwave
from synthDriverHandler import synthChanged

# Import Steam Audio
try:
	from . import steam_audio
except ImportError as e:
	log.error(f"Failed to load Steam Audio: {e}")
	raise

UNSPOKEN_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


# Sounds

UNSPOKEN_SOUNDS_PATH = os.path.join(UNSPOKEN_ROOT_PATH, "sounds")

sounds = dict()  # For holding instances in RAM.


# taken from Stackoverflow. Don't ask.
def clamp(my_value, min_value, max_value):
	return max(min(my_value, max_value), min_value)


class UnspokenPlayer:
	def __init__(self, *args, **kwargs):
		super(UnspokenPlayer, self).__init__(*args, **kwargs)
		config.conf.spec["unspoken"] = {
			"sayAll": "boolean(default=False)",
			"speakRoles": "boolean(default=False)",
			"noSounds": "boolean(default=False)",
			"HRTF": "boolean(default=True)",
			"volumeAdjust": "boolean(default=True)",
			"Reverb": "boolean(default=True)",
			"RoomSize": "integer(default=10, min=0, max=100)",
			"Damping": "integer(default=100, min=0, max=100)",
			"WetLevel": "integer(default=9, min=0, max=100)",
			"DryLevel": "integer(default=30, min=0, max=100)",
			"Width": "integer(default=100, min=0, max=100)",
		}
		log.debug("Initializing Steam Audio", exc_info=True)
		self.steam_audio = steam_audio.get_steam_audio()
		if not self.steam_audio.initialize():
			log.error("Failed to initialize Steam Audio")
			raise RuntimeError("Steam Audio initialization failed")

		# Configure reverb settings
		self.steam_audio.set_reverb_settings(
			room_size=config.conf["unspoken"]["RoomSize"] / 100.0,
			damping=config.conf["unspoken"]["Damping"] / 100.0,
			wet_level=config.conf["unspoken"]["WetLevel"] / 100.0,
			dry_level=config.conf["unspoken"]["DryLevel"] / 100.0,
			width=config.conf["unspoken"]["Width"] / 100.0,
		)

		# Initialize WavePlayer for audio output (stereo, 44100Hz, 16-bit)
		self.create_wave_player()
		self._last_played_object = None
		self._last_played_time = 0
		self._last_navigator_object = None

		# these are in degrees.
		self._display_width = 180.0
		self._display_height_min = -40.0
		self._display_height_magnitude = 50.0
		synthChanged.register(self.on_synthChanged)
		self.audio3d = True
		self.use_in_say_all = True
		self.speak_roles = False
		self.use_synth_volume = True
		self.volume = 100
		self._reverb = config.conf["unspoken"]["Reverb"]
		self._room_size = config.conf["unspoken"]["RoomSize"]
		self._damping = config.conf["unspoken"]["Damping"]
		self._wet_level = config.conf["unspoken"]["WetLevel"]
		self._dry_level = config.conf["unspoken"]["DryLevel"]
		self._width = config.conf["unspoken"]["Width"]

	@property
	def reverb(self):
		return self._reverb

	@reverb.setter
	def reverb(self, value):
		if self._reverb != value:
			self._reverb = value
			self._update_reverb_settings()

	@property
	def room_size(self):
		return self._room_size

	@room_size.setter
	def room_size(self, value):
		if self._room_size != value:
			self._room_size = value
			self._update_reverb_settings()

	@property
	def damping(self):
		return self._damping

	@damping.setter
	def damping(self, value):
		if self._damping != value:
			self._damping = value
			self._update_reverb_settings()

	@property
	def wet_level(self):
		return self._wet_level

	@wet_level.setter
	def wet_level(self, value):
		if self._wet_level != value:
			self._wet_level = value
			self._update_reverb_settings()

	@property
	def dry_level(self):
		return self._dry_level

	@dry_level.setter
	def dry_level(self, value):
		if self._dry_level != value:
			self._dry_level = value
			self._update_reverb_settings()

	@property
	def width(self):
		return self._width

	@width.setter
	def width(self, value):
		if self._width != value:
			self._width = value
			self._update_reverb_settings()

	def _update_reverb_settings(self):
		self.steam_audio.set_reverb_settings(
			room_size=self._room_size / 100.0,
			damping=self._damping / 100.0,
			wet_level=self._wet_level / 100.0,
			dry_level=self._dry_level / 100.0,
			width=self._width / 100.0,
		)

	def create_wave_player(self):
		self.wave_player = nvwave.WavePlayer(
			channels=2,
			samplesPerSec=44100,
			bitsPerSample=16,
			outputDevice=config.conf["audio"]["outputDevice"],
		)

	def make_sound_object(self, path):
		"""Load sound files for Steam Audio processing."""
		log.debug("Loading sound files for Steam Audio", exc_info=True)
		log.debug("Loading " + path, exc_info=True)
		try:
			# Load WAV file and convert to float32 mono
			with wave.open(path, "rb") as wav_file:
				frames = wav_file.readframes(wav_file.getnframes())
				sample_width = wav_file.getsampwidth()
				channels = wav_file.getnchannels()
				sample_rate = wav_file.getframerate()

				# Convert to float32 samples
				if sample_width == 2:  # 16-bit
					import struct

					samples = struct.unpack(f"<{len(frames) // 2}h", frames)
					float_samples = [s / 32768.0 for s in samples]
				else:
					log.error(f"Unsupported sample width: {sample_width}")
					return None

				# Convert to mono if stereo
				if channels == 2:
					float_samples = [
						float_samples[i] for i in range(0, len(float_samples), 2)
					]

				return {"data": float_samples, "sample_rate": sample_rate}

		except Exception as e:
			log.error(f"Failed to load {path}: {e}")
			return None

	def _compute_volume(self):
		if not self.use_synth_volume:
			return self.volume / 100.0
		driver = speech.speech.getSynth()
		volume = getattr(driver, "volume", 100) / 100.0  # nvda reports as percent.
		volume = clamp(volume, 0.0, 1.0)
		return volume if not config.conf["unspoken"]["HRTF"] else volume + 0.25

	def _play_audio_data(self, audio_bytes):
		"""Play processed audio data using nvwave.WavePlayer in a thread"""

		def play_in_thread():
			try:
				self.wave_player.feed(audio_bytes)
			except Exception as e:
				log.error(f"Failed to play audio: {e}")

		# Play audio in a separate thread to avoid blocking
		threading.Thread(target=play_in_thread, daemon=True).start()

	def play(self, obj, sound):
		if config.conf["unspoken"]["noSounds"]:
			return
		if self.use_in_say_all and SayAllHandler.isRunning():
			return
		curtime = time.time()
		if self._last_played_object and (curtime - self._last_played_time < 0.2 and obj.name == self._last_played_object.name):
			return
		self._last_played_object = obj
		self._last_played_time = curtime
		role = obj.role
		if self.audio3d:
			# Get coordinate bounds of desktop.
			desktop = NVDAObjects.api.getDesktopObject()
			desktop_max_x = desktop.location[2]
			desktop_max_y = desktop.location[3]
			# Get location of the object.
			if obj.location != None:
				# Object has a location. Get its center.
				obj_x = obj.location[0] + (obj.location[2] / 2.0)
				obj_y = obj.location[1] + (obj.location[3] / 2.0)
			else:
				# Objects without location are assumed in the center of the screen.
				obj_x = desktop_max_x / 2.0
				obj_y = desktop_max_y / 2.0
			# Scale object position to audio display.
			angle_x = (
				(obj_x - desktop_max_x / 2.0) / desktop_max_x
			) * self._display_width
			# angle_y is a bit more involved.
			percent = (desktop_max_y - obj_y) / desktop_max_y
			angle_y = (
				self._display_height_magnitude * percent + self._display_height_min
			)
			# clamp these to Libaudioverse's internal ranges.
			angle_x = clamp(angle_x, -90.0, 90.0)
			angle_y = clamp(angle_y, -90.0, 90.0)
		else:
			angle_x = 0
			angle_y = 0
		# Process audio with Steam Audio
		sound_data = sound
		audio_data = sound_data["data"]
		# Adjust volume
		volume = self._compute_volume()
		adjusted_audio = [sample * volume for sample in audio_data]

		# Process with Steam Audio for 3D positioning (without reverb)
		processed_audio = self.steam_audio.process_sound(
			adjusted_audio, angle_x, angle_y
		)
		if not processed_audio:
			return

		# Apply reverb if enabled
		final_audio = processed_audio
		if config.conf["unspoken"]["Reverb"]:
			reverb_audio = self.steam_audio.apply_reverb(processed_audio)
			if reverb_audio:
				final_audio = reverb_audio
			else:
				pass

		# Play the final audio
		self.wave_player.stop()
		self._play_audio_data(final_audio)

	def play_file(self, path):
		sound = self.make_sound_object(path)
		if not sound:
			return
		# Process audio with Steam Audio
		audio_data = sound["data"]
		# Adjust volume
		volume = self._compute_volume()
		adjusted_audio = [sample * volume for sample in audio_data]

		if self.audio3d:
			# Process with Steam Audio for 3D positioning (without reverb)
			processed_audio = self.steam_audio.process_sound(
				adjusted_audio, 0, 0
			)
			if not processed_audio:
				return

			# Apply reverb if enabled
			final_audio = processed_audio
			if config.conf["unspoken"]["Reverb"]:
				reverb_audio = self.steam_audio.apply_reverb(processed_audio)
				if reverb_audio:
					final_audio = reverb_audio
				else:
					pass
		else:
			# convert to stereo 16-bit
			final_audio = b""
			for sample in adjusted_audio:
				sample = int(sample * 32767)
				final_audio += struct.pack("<h", sample)
				final_audio += struct.pack("<h", sample)

		# Play the final audio
		self.wave_player.stop()
		self._play_audio_data(final_audio)

	def terminate(self):
		# Close WavePlayer
		if hasattr(self, "wave_player"):
			try:
				self.wave_player.close()
			except:
				pass

		# Cleanup Steam Audio
		if hasattr(self, "steam_audio"):
			self.steam_audio.cleanup()
		synthChanged.unregister(self.on_synthChanged)

	def on_synthChanged(self):
		self.wave_player.close()
		self.create_wave_player()
