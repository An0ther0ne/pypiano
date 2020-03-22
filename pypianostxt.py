﻿#-*- coding: utf-8 -*-

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
notemul = 2 ** (1/12)
pianokeys = {
	59  : notestd['C'],
	60  : notestd['C'] * notemul, # C#
	61  : notestd['D'],
	62  : notestd['D'] * notemul, # D#,
	63  : notestd['E'],
	64  : notestd['F'],
	65  : notestd['F'] * notemul, # F#,
	66  : notestd['G'],
	67  : notestd['G'] * notemul, # G#,
	68  : notestd['A'],
	133 : notestd['A'] * notemul, # A#,
	134 : notestd['B'],
}

# --- procs

def callback(outdata, frames, t, status):
	global start_idx, frequency, oldfreq
	tt = (start_idx + np.arange(frames)) / samplerate
	tt = tt.reshape(-1, 1)
	if oldfreq == frequency:
		outdata[:] = amplitude * np.sin(2 * np.pi * frequency * tt)
		# start_idx = (start_idx + frames) % samplerate
		start_idx = (start_idx + frames) % (samplerate / frequency)
	else: # for seamless frequency transition and noise reduction 
		data = amplitude * np.sin(2 * np.pi * oldfreq * tt)
		for i,v in enumerate(data):
			if i > 0 and v < 0 and v > -0.01 and (v - data[i-1]) > 0:
				tt = np.arange(frames - i) / samplerate
				tt = tt.reshape(-1, 1)
				start_idx = frames - i
				data[i:] = amplitude * np.sin(2 * np.pi * frequency * tt)
				break
		outdata[:] = data
		oldfreq = frequency
	
def helpmsg():
	print('#' * 80)
	print("Controll keys:")
	print("'ESC'      : Exit")
	print("'+'        : Increase volume by 25%")
	print("'-'        : Decrease volume by 25%")
	print("'PgUp'     : Octave + 1")
	print("'PgDn'     : Octave - 1")
	print("'Up'       : Current frequency + 1%")
	print("'Down'     : Current frequency - 1%")
	print('-' * 80)
	print("'F1'-'F12' : Piano keys: C C# D D# E F F# G G# A A# B")
	print('-' * 80)
	for k in notes.keys():
		print("'{}'        : Play note {}".format(k,k))
	print('#' * 80)
	
# --- decorate print

pprint = print; print = lambda *args, **kwargs : pprint(flush=True, *args, **kwargs)
helpmsg()

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
			elif chr(key & 0xDF) in notes.keys():
				frequency = notes[chr(key & 0xDF)]
			elif key == 0:		# Special functional key pressed
				key = int.from_bytes(msvcrt.getch(), 'little', signed=False)
				if key in pianokeys.keys(): # F1 - F10
					frequency = pianokeys[key]
				elif DEBUG: 
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
				elif DEBUG: 
					print("Special key '{}' pressed".format(key))
			elif key != 255:
				if DEBUG: print("key={}, key|0x20={}, key&0xDF={}".format(key, key|0x20, key&0xDF))
		sd.sleep(10)
		