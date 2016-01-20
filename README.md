# tonic_identifier
An Automatic Tonic Identification Method for Turkish Makam Music Recordings

Introduction
=======
This repository hosts the implementation of the tonic identification method proposed for makam music in:

_Atlı, H. S., Bozkurt B., and Şentürk S. (2015). A method for tonic frequency identification of Turkish makam music recordings. 5th International Workshop on Folk Music Analysis (FMA)._

If you are using this identifier please cite the above paper. 

Tonic is the final tone in the Turkish makam music performances. The methodology implemented in this repository is based on detecting the last note in the recording and estimating its frequency. 

Usage
=======
```python
import json
from tonic_identifier.tonic_identifier import TonicLastNote
from pitchfilter.pitchfilter import PitchPostFilter

pitch = json.load(open("sample_data/cab08727-d5c2-4fda-9d96-d107915a85ec.json", 'r'))['pitch']

# Post process the pitch track to get rid of spurious pitch estimations and correct octave errors
flt = PitchPostFilter()
pitch = flt.run(pitch)

tonic_identifier = TonicLastNote()
tonic, pitch, pitch_chunks, distribution, stable_pitches = tonic_identifier.identify(pitch)
print tonic
```

Please refer to demo.ipynb for an interactive demo.

Installation
============

If you want to install the repository, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then install the repo like this instead

    pip install -e .

The algorithm uses some modules in Essentia. Follow the [instructions](essentia.upf.edu/documentation/installing.html) to install the library. Then you should link the python bindings of Essentia in the virtual encironment:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Then you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
