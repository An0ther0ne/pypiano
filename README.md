# pypiano

Play generated wave sound with Python and Sounddevice module.

## Video demo

[![Youtube video](img/pypianoy.png)](https://www.youtube.com/embed/-wZeW_NdPNw)

## Features:

* Initialy octave number is 4.
* Special algorithm for seamless frequency transition and noise reduction
* Use callback procedure for directly calculate sound waveform
* Sine, square, saw, trapeze or triangle waveforms
* Additional tools for watch form and spectrum audio signal

## Used keys:

### For control

| Keys | Desctiption |
| --- | --- |
| ESC | Exit |
| + | Increase volume |
| - | Decrease volume |
| PgUp | Octave + 1 |
| PgDn | Octave - 1 |
| Up | Current frequency + 1% |
| Down | Current frequency - 1% |
| [ ] | Square wave form |
| ~ | Sine wave form |
| < > | Triangle waveform |
| / | Saw waveform |
| = | Trapeze waveform |

### Piano mapped keys:

Note: The frequencies are listed for the fourth octave.

| Key | Piano note | Frequency, Hz |
| --- | --- | --- |
| F1 | C | 261.6256 |
| F2 | C# | 277.1826 |
| F3 | D | 293.6648 |
| F4 | D# | 311.1270
| F5 | E | 329.6276 |
| F6 | F | 349.2282 |
| F7 | F# | 369.9944 |
| F8 | G | 391.9954 |
| F9 | G# | 415.3047 |
| F10 | A | 440.0 |
| F11 | A# | 466.1638 |
| F12 | B | 493.8833 |

### Directly named

| Key | Note | Frequency, Hz |
| --- | --- | --- |
| D | D | 293.6648 |
| A | A | 440.0 | 
| C | C | 261.6256 |
| E | E | 329.6276 |
| F | F | 349.2282 |
| B | B | 493.8833 |
| G | G | 391.995 |

## Requirements:

* Python
* NumPY
* sounddevice

## Files:
	
* [pypianostxt.py](pypianostxt.py) - Text mode sine wave generator
* [waveform.py](waveform.py) - Simple GUI tool for watch sound waveform with matplotlib
* [spectrogram.py](spectrogram.py) - Simple spectrogram tool like fire uses opencv
* README.md - This readme file
* LICENSE - MIT LICENSE

# AUTHOR
   An0ther0ne
