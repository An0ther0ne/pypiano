#-*- coding: utf-8 -*-

import numpy as np
import sounddevice as sd
import msvcrt
from functools import reduce

# --- globals

DEBUG = True
samplerate  = 44100
frequency   = 77.7
oldfreq     = frequency
amplitude   = 0.5
channels    = 2
start_idx   = 0
octavenum   = 4
attenuateex = 0.9		# attenuation factor (multiplier)
attenuation = False

# --- notes

notestd = {
	'B' : 493.8833,
	'A' : 440.0,
	'G' : 391.995,
	'F' : 349.2282,
	'E' : 329.6276,
	'D' : 293.6648,
	'C' : 261.6256,
}
notes = notestd.copy()

# --- classes

class Wave:
	_samplerate  = 44100
	_channels = 2
	_amplitude = 0.5
	_frequency = 77.7
	_oldfreq = _frequency
	_waveformnum = 0
	_start_idx = 0
	def _set_amplitude(self, a):
		if a > 0 and a < 1: 
			self._amplitude = a
	def _sine(self):
		pass
	def _square(self):
		pass
	def _saw(self):
		pass
	def _triangle(self):
		pass
	def _trapeze(self):
		pass
	def _triangle(self):
		pass	
	_waveforms = {
		0 : _sine,
		1 : _square,
		2 : _saw,
		3 : _triangle,
		4 : _trapeze,
	}
	def _callback(outdata, frames, t, status):
		def getsounddata(freq, tfrom, tto, idx):
			def getframes():
				tt = (idx + np.arange(tfrom - tto)) / self._samplerate
				return tt.reshape(-1, 1)
			return wave(freq, getframes)
		if self._oldfreq == self._frequency:
			data = getsounddata(self._frequency, frames, 0, self._start_idx)
			self._start_idx = (self._start_idx + frames) % (self._samplerate / self._frequency)
		else: # for seamless frequency transition and noise reduction 
			data = getsounddata(self._oldfreq, frames, 0, self._start_idx)
			for i,v in enumerate(data):
				if i > 0 and v < 0 and v > -0.01 and (v - data[i-1]) > 0:
					self._start_idx = frames - i
					data[i:] = getsounddata(self._frequency, frames, i, 0)
					break
			self._oldfreq = self._frequency
		outdata[:] = data
	def NextWaveForm(self):
		self._waveformnum = (self._waveformnum + 1) % len(self._waveforms)
		self.wave =	self._waveforms[self._waveformnum]
	def PrevWaveForm(self):
		self._waveformnum = (self._waveformnum - 1) % len(self._waveforms)
		self.wave =	self._waveforms[self._waveformnum]
	def Play(self):
		pass
	amplitude = property(lambda self : self._amplitude, _set_amplitude)
	wave = property(lambda self : _waveforms[_waveformnum])
	callback = property(lambda self : _callback)
	channels = property(lambda self : _channels)
	samplerate = property(lambda self : _samplerate)

class Note(Wave):
	def __init__(self, fr, at, wf):	# freequency, attenuation, waveform
		self._frequency  = fr
		self._attenuation = at
		self._waveformnum  = wf
	def _play(self):
		Wave.Play()
	def PlayFreq(self, freq):
		self._frequency = freq
	def PlayNoteByName(self, NoteName):
		pass
	def PlayNoteByNum(self, NoteNum):
		pass

class Octave:
	'''Controll keys:
'ESC'      : Exit
'Tab'      : Toggle attenuation
'+'        : Increase volume by 25%
'-'        : Decrease volume by 25%
'PgUp'     : Octave + 1
'PgDn'     : Octave - 1
'Up'       : Current frequency + 1%
'Down'     : Current frequency - 1%
'Home'     : Next waveform
'End'	   : Previous waveform
'[' | ']'  : Square waveform
'~'        : Sine waveform
'<' | '>'  : Triangle waveform
'/'        : Saw waveform
'='        : Trapeze waveform'''
	_gamma     = "C Cs D Ds E F Fs G Gs A As B".split()
	_scancodes = [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 133, 134] # F1 - F12
	_octavenum = 4
	def _recalc(self):
		baseA = 55.0 * 2 ** (self._octavenum - 1)
		for num, note in enumerate(self._gamma):
			self._notesfreq[note] = baseA * 2 ** ((num - 9) / 12)
	def __init__(self):
		self._notesfreq = {}
		self._recalc()
	def Next(self):
		if self._octavenum < 9:
			self._octavenum += 1
			self._recalc()
	def Prev(self):
		if self._octavenum > 1:
			self._octavenum -= 1
			self._recalc()
	def Set(self, num):
		if num > 0 and num < 10:
			self._octavenum = num
			self._recalc()
	def GetNote(self, note):
		if note in self._gamma:
			return self._notesfreq[note]
		else:
			return None
	def GetNoteNum(self, num):
		if num >= 0 and num < 12:
			return self._notesfreq[self._gamma[num]]
		else:
			return None
	def __str__(self):
		return reduce(
			lambda i,j : i + ['', "\n"][len(i) > 0] + "'{}'\t   : Play note {}".format(j,j),
			filter(lambda x : len(x) == 1, self._gamma),
			'')
	def HelpMsg(self):
		print('#' * 80)
		print(self.__doc__)
		print('-' * 80)
		print("'F1'-'F12' : Piano keys:", 
			reduce(lambda i,j : i + ' ' + j, self._gamma).replace('s','#'))
		print('-' * 80)
		print(self)
		print('#' * 80)		
		
# --- procs

def get_piano_notes(octave):
	pkeys = {}
	baseA = 55.0 * 2 ** (octave - 1)
	for k in [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 133, 134]:
		if k < 68:
			pkeys[k] = baseA * 2 ** ((k - 68)/12) 
		elif k == 68:
			pkeys[k] = baseA	# note A4
		else:
			pkeys[k] = baseA * 2 ** ((k - 132)/12)	
	return pkeys
	
def getamplitude(freq, frames):
	if attenuation:
		amp = np.linspace(amplitude, amplitude, num=len(frames))
	else:
		amp = np.linspace(amplitude, amplitude, num=len(frames))
	return amp.reshape(-1,1)

def sine(freq, frames):
	f = frames()
	return getamplitude(freq, f) * np.sin(2 * np.pi * freq * f)
	
def square(freq, frames):
	f = frames()
	amp = getamplitude(freq, f)
	w = (2 * freq * f).astype(int)
	ww = w.astype(float)
	for i,v in enumerate(w):
		if v % 2 == 0:
			ww[i] = amp[i]
		else:
			ww[i] = -amp[i]
	return ww.reshape(-1,1)

def saw(freq, frames):
	f = frames()
	w = (2 * freq * f) % 2
	w = (w * 2 - 1) * getamplitude(freq, f) / 2
	return w
	
def triangle(freq, frames):
	f = frames()
	return 2 * getamplitude(freq, f) * np.arcsin(np.sin(2 * np.pi * freq * f)) / np.pi

def trapeze(freq, frames):
	f = frames()
	t = np.arcsin(np.sin(2 * np.pi * freq * f))
	return getamplitude(freq, f) * np.where(t > 1, 1, np.where(t < -1, -1, t))

def callback(outdata, frames, t, status):
	global start_idx, frequency, oldfreq
	def getsounddata(freq, tfrom, tto, idx):
		def getframes():
			tt = (idx + np.arange(tfrom - tto)) / samplerate
			return tt.reshape(-1, 1)
		return wave(freq, getframes)
	if oldfreq == frequency:
		data = getsounddata(frequency, frames, 0, start_idx)
		start_idx = (start_idx + frames) % (samplerate / frequency)
	else: # for seamless frequency transition and noise reduction 
		data = getsounddata(oldfreq, frames, 0, start_idx)
		for i,v in enumerate(data):
			if i > 0 and v < 0 and v > -0.01 and (v - data[i-1]) > 0:
				start_idx = frames - i
				data[i:] = getsounddata(frequency, frames, i, 0)
				break
		oldfreq = frequency
	outdata[:] = data

# --- decorate print and other initialisation

pprint = print; print = lambda *args, **kwargs : pprint(flush=True, *args, **kwargs)

# --- implementation

octave = Octave()
octave.HelpMsg()
	
pianokeys = get_piano_notes(octavenum)
waveforms = {
	0 : ['Sine'  , sine],
	1 : ['Square', square],
	2 : ['Saw',    saw],
	3 : ['Three',  triangle],
	4 : ['Trapeze',trapeze],
}
wformnum = 0
wave = waveforms[wformnum][1]

# --- main cycle

with sd.OutputStream(channels=channels, callback=callback, samplerate=samplerate):
	while True:
		if msvcrt.kbhit():
			key = int.from_bytes(msvcrt.getch(), 'little', signed=False)
			if  key == 27: # ESC'
				break
			elif key == 9:			# Tab
				attenuation = not attenuation
			elif key == ord('+'):
				amplitude *= 1.25
				if amplitude > 1:
					amplitude = 1
			elif key == ord('-'):
				amplitude /= 1.25
			elif key in [44, 46, 47, 61, 91, 93, 96]: 	# []~/=
				if key in [91,93]:		# []
					wformnum = 1
				elif key in [44,46]:
					wformnum = 2
				elif key == 96:			# ~
					wformnum = 0
				elif key == 47:			# /
					wformnum = 3
				elif key == 61:			# =
					wformnum = 4
				wave = waveforms[wformnum][1]
			elif chr(key & 0xDF) in notes.keys():
				frequency = notes[chr(key & 0xDF)]
			elif key == 0:		# Special functional key pressed
				key = int.from_bytes(msvcrt.getch(), 'little', signed=False)
				if key in pianokeys.keys(): # F1 - F10
					frequency = pianokeys[key]
				if DEBUG: 
					print("Special functional key '{}' pressed".format(key))
			elif key == 224:	# Special key pressed
				key = int.from_bytes(msvcrt.getch(), 'little', signed=False)
				if key in pianokeys.keys(): # F11 - F12
					frequency = pianokeys[key]
				elif key == 73:   # PgUp
					if octavenum < 9:
						octavenum += 1
						frequency *= 2
						for k in notes.keys():
							notes[k] *= 2
				elif key == 81:   # PgDn
					if octavenum > 1:
						octavenum -= 1
						frequency /= 2
						for k in notes.keys():
							notes[k] /= 2
				elif key == 72:   # Up
					frequency *= 1.01
				elif key == 80:   # Down
					frequency /= 1.01
				elif key in [71,79]:
					if key == 71: 		# Home
						wformnum = (wformnum + 1) % len(waveforms)
					elif key == 79: 	# End
						wformnum = (wformnum - 1) % len(waveforms)
					wave = waveforms[wformnum][1]
				if DEBUG:
					print("Special key '{}' pressed".format(key))
				if key in [73, 81]:
					if octavenum == 4:
						notes = notestd.copy()
					pianokeys = get_piano_notes(octavenum)
			if key != 255:
				if DEBUG: 
					print("key={}, key|0x20={}, key&0xDF={}".format(key, key|0x20, key&0xDF))
				if frequency != oldfreq or key in [ord('+'), ord('-')]:
					print("Freq={:5.4f} Octave={:1} Volume={:3.1f}%".format(frequency, octavenum, amplitude * 100))
		sd.sleep(10)
		