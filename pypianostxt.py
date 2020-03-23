#-*- coding: utf-8 -*-

import numpy as np
import sounddevice as sd
import msvcrt

# --- globals

DEBUG = True
samplerate = 44100
frequency  = 100
oldfreq    = frequency
amplitude  = 0.1
channels   = 2
start_idx  = 0
octavenum  = 4

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

def sine(freq, frames):
	return amplitude * np.sin(2 * np.pi * freq * frames())
	
def square(freq, frames):
	w = frames().reshape(-1)
	w = 2 * freq * w
	w = w.astype(int)
	ww = np.where(w % 2 == 0, amplitude, -amplitude)
	return ww.reshape(-1,1)

def callback(outdata, frames, t, status):
	global start_idx, frequency, oldfreq
	def getsounddata(freq, tfrom, tto, idx):
		def getframes():
			tt = (idx + np.arange(tfrom - tto)) / samplerate
			return tt.reshape(-1, 1)
		return wave(freq, getframes)
	if oldfreq == frequency:
		outdata[:] = getsounddata(frequency, frames, 0, start_idx)
		start_idx = (start_idx + frames) % (samplerate / frequency)
	else: # for seamless frequency transition and noise reduction 
		data = getsounddata(oldfreq, frames, 0, start_idx)
		for i,v in enumerate(data):
			if i > 0 and v < 0 and v > -0.01 and (v - data[i-1]) > 0:
				start_idx = frames - i
				data[i:] = getsounddata(frequency, frames, i, 0)
				break
		outdata[:] = data
		oldfreq = frequency
	
def helpmsg():
	print('#' * 80)
	print('''Controll keys:
'ESC'      : Exit")
'+'        : Increase volume by 25%")
'-'        : Decrease volume by 25%")
'PgUp'     : Octave + 1")
'PgDn'     : Octave - 1")
'Up'       : Current frequency + 1%")
'Down'     : Current frequency - 1%")
'Home'     : Next wave form
'End'	   : Previous wave form
'[' | ']'  : Square wave form
'~'        : Sine wave form
'<' | '>'  : Triangle wave form''')
	print('-' * 80)
	print("'F1'-'F12' : Piano keys: C C# D D# E F F# G G# A A# B")
	print('-' * 80)
	for k in notes.keys():
		print("'{}'        : Play note {}".format(k,k))
	print('#' * 80)
	
# --- decorate print and other initialisation

pprint = print; print = lambda *args, **kwargs : pprint(flush=True, *args, **kwargs)
helpmsg()
pianokeys = get_piano_notes(octavenum)
waveforms = {
	0 : ['Sine'  , sine],
	1 : ['Square', square],
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
			elif key == ord('+'):
				amplitude *= 1.25
				if amplitude > 1:
					amplitude = 1
			elif key == ord('-'):
				amplitude /= 1.25
			elif key in [91, 93, 96]: 	# []~
				if key in [91,93]:		# []
					wformnum = 1
				elif key == 96:			# ~
					wformnum = 0
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
		