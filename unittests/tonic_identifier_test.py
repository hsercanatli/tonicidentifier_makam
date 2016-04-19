import os
import numpy
import json
from tonicidentifier.toniclastnote import TonicLastNote


def test_tonic_identification():
    pitch = numpy.array(json.load(open(os.path.join(
        "sample_data", "cab08727-d5c2-4fda-9d96-d107915a85ec.json"),
        'r'))['pitch'])

    tonic_identifier = TonicLastNote()
    tonic, pitch, pitch_chunks, pitch_distribution, stable_pitches = \
        tonic_identifier.identify(pitch)

    saved_tonic = json.load(open(os.path.join(
        'sample_data', 'cab08727-d5c2-4fda-9d96-d107915a85ec_tonic.json'),
        'r'))

    assert (numpy.isclose(tonic['value'], saved_tonic['value']))
