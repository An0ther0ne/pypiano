'''To capture audio from speakers select and turn on stereo mixer'''
import queue
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

channels	= 1			# output channels to plot
# channels	= 2			# output channels to plot
DURATION 	= 100		# visible time slot, ms
interval	= 20		# minimum time between plot updates, ms
downsample	= 10		# display every Nth sample
samplerate	= 44100		# sampling rate of audio device

mapping = [c - 1 for c in range(channels)]
q = queue.Queue()

def audio_callback(indata, frames, ttime, status):
	q.put(indata[::downsample, mapping])

def update_plot(frame):
	global plotdata
	while True:
		try:
			data = q.get_nowait()
		except queue.Empty:
			break
		shift = len(data)
		plotdata = np.roll(plotdata, -shift, axis=0)
		plotdata[-shift:, :] = data
	for column, line in enumerate(lines):
		line.set_ydata(plotdata[:, column])
	return lines

try:
	length = int(DURATION * samplerate / (1000 * downsample))
	plotdata = np.zeros((length, channels))
	fig, ax = plt.subplots()
	lines = ax.plot(plotdata)
	if channels > 1:
		ax.legend(['channel {}'.format(c+1) for c in range(channels)])
	ax.axis((0, len(plotdata), -1, 1))
	ax.set_yticks([0])
	ax.yaxis.grid(True)
	ax.tick_params(bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
	fig.tight_layout(pad=0)
	stream = sd.InputStream(
		# device     = OutputDevice,
		channels   = channels,
		# samplerate = samplerate,
		callback   = audio_callback
	)
	ani = FuncAnimation(fig, update_plot, interval=interval, blit=True)
	with stream:
		plt.gcf().canvas.set_window_title('Waveform from input')
		plt.show()
except Exception as e:
	pass
