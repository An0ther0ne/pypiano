import math
import shutil
import numpy as np
import cv2
import sounddevice as sd

DEBUG = False
helpstr = "Press ESC/'q' to quit, '+' / '-' to change scaling."

duration	= 50
devicenum	= 1
channels    = 1
gain		= 128
low			= 100
high		= 2000
colors		= 30, 34, 35, 91, 93, 97

title   = 'Runtime microphone spectrogtram'
height  = 200
width   = 800
zeros   = np.zeros((height, width), dtype="uint8")
frame   = np.copy(zeros)
firerow = np.empty(width, dtype="uint8")

dotsize = 5
columns = width // dotsize

print(helpstr, flush=True)

try:
	inputdevice = sd.query_devices(devicenum, 'input')
	if DEBUG:
		print('Input device:', flush=True)
		for k in inputdevice.keys():
			print("\t{} = {}".format(k, inputdevice[k]), flush=True)
	samplerate = inputdevice['default_samplerate']
	delta_f = (high - low) / columns
	fftsize = math.ceil(samplerate / delta_f)
	low_bin = math.floor(low / delta_f)
	if DEBUG:
		print("+++ fftsize=", fftsize, flush=True)
		print("+++ samplerate=", samplerate, flush=True)
		print("+++ delta_f=", delta_f, flush=True)
	def callback(indata, frames, ttime, status):
		global frame
		if status and DEBUG:
			print('+++ Status: ' + str(status), flush=True)
		if any(indata):
			magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
			magnitude *= gain / fftsize
			for i, x in enumerate(magnitude[low_bin:low_bin + columns]):	# columns elements
				color = np.uint8(np.clip(x, 0, 1) * 255)
				xshift = i * dotsize
				for y in range(dotsize):
					firerow[xshift + y] = color
			frame[-1] = firerow
			for i in range(height-1):
				frame[i,:] = frame[i+1,:]			
			for i in range(height-1):
				frame[i,:] = (frame[i+1,:] >> 1) + (frame[i,:] >> 1)
			# frame = cv2.GaussianBlur(frame, (3,7), 0)
			frame = cv2.GaussianBlur(frame, (3,5), 0)
			
	with sd.InputStream(device=devicenum, channels=channels, callback=callback, blocksize=int(samplerate * duration / 1000), samplerate= samplerate):
		while True:
			key = cv2.waitKey(10) & 0xFF
			if  key | 0x20 == ord('q') or key == 27: # 'q' or 'Q ' or 'ESC'
				break
			elif key == 43:	# '+'
				gain *= 2
			elif key == 45:	# '-'
				gain /= 2
			elif key != 255:
				print("key={} ".format(key) + helpstr, flush=True)
			rframe = np.uint8(16*np.sqrt(frame))
			videoframe = cv2.merge([zeros, frame, rframe])
			cv2.imshow(title, videoframe)
		
except KeyboardInterrupt:
	print('Interrupt by user')
except Exception as e:
	print(str(e))

