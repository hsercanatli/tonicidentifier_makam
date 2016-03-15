import os
import numpy
import json
from pitchfilter.PitchFilter import PitchFilter
from tonicidentifier.TonicLastNote import TonicLastNote


def test_tonic_identification():
    pitch = numpy.array(json.load(open(os.path.join(
        "sample_data", "e72db0ad-2ed9-467b-88ae-1f91edcd2c59.json"),
        'r'))['pitch'])

    # Post process the pitch track to get rid of spurious pitch estimations
    # and correct octave errors
    flt = PitchFilter()
    pitch = flt.run(pitch)

    tonic_identifier = TonicLastNote()
    tonic, pitch, pitch_chunks, pitch_distribution, stable_pitches = \
        tonic_identifier.identify(pitch)

    saved_tonic = numpy.array(json.load(open(os.path.join(
        'sample_data', 'cab08727-d5c2-4fda-9d96-d107915a85ec_tonic.json'),
        'r')))

    assert tonic == saved_tonic
