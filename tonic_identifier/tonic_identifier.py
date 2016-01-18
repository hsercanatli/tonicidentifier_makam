# -*- coding: utf-8 -*-
__author__ = 'hsercanatli'

from numpy import median
from numpy import where
import numpy as np
import PitchDistribution
from pitchfilter.pitchfilter import PitchPostFilter

import matplotlib.pyplot as plt
import matplotlib.ticker

class TonicLastNote:
    def __init__(self, kernel_width=7.5, step_size=7.5, min_freq=64, max_freq=1024, 
                 lower_interval_thres=0.965, upper_interval_thres=1.035, min_chunk_size=60):

        self.kernel_width = kernel_width  # cents, kernel width of the pitch distribution, ~1/3 Holderian comma
        self.step_size = step_size  # cents, step size of the bins of the pitch distribution, ~1/3 Holderian comma

        self.min_freq = min_freq  # minimum frequency allowed
        self.max_freq = max_freq  # maximum frequency allowed
        self.lower_interval_thres = lower_interval_thres  # the smallest value the interval can stay before a new chunk is formed
        self.upper_interval_thres = upper_interval_thres  # the highest value the interval can stay before a new chunk is formed
        self.min_chunk_size = min_chunk_size  # minimum number of samples to form a chunk

    @staticmethod
    def find_nearest(array, value):
        distance = [abs(element - value) for element in array]
        idx = distance.index(min(distance))
        return array[idx]

    def identify(self, pitch, plot=False, verbose=False):
        """
        Identify the tonic by detecting the last note and extracting the frequency
        """
        tonic = 0
        octave_wrapped = 1

        # convert Hz to cent using a dummy value for distribution computation
        dummyFreq = 440.0
        pitch = np.array(pitch)
        tempCentVals = PitchDistribution.hz_to_cent(pitch[:,1], dummyFreq)

        # compute the pitch distribution and distribution peaks
        distribution = PitchDistribution.generate_pd(tempCentVals, ref_freq=dummyFreq, 
            kernel_width=self.kernel_width, step_size=self.step_size)
        distribution.bins = PitchDistribution.cent_to_hz(distribution.bins, 
            dummyFreq)

        # get the stable pitches
        peaks = distribution.detect_peaks()
        peakId = peaks[0]
        stable_pitches = distribution.bins[peakId]

        # get pitch chunks
        flt = PitchPostFilter(lower_interval_thres=self.lower_interval_thres, 
                              upper_interval_thres=self.upper_interval_thres,
                              min_freq=self.min_freq, max_freq=self.max_freq)
        pitch_chunks = flt.decompose_into_chunks(pitch)
        pitch_chunks = flt.post_filter_chunks(pitch_chunks)

        cnt = 1
        while tonic is 0:
            last_chunk = [element[1] for element in pitch_chunks[-cnt]]

            last_note = median(last_chunk)
            stable_pitches = sorted(stable_pitches, key=lambda x: abs(last_note - x))

            for j in range(len(stable_pitches)):
                tonic_candidate = float(stable_pitches[j])

                if (tonic_candidate / (2 ** (2. / 53))) <= last_note <= (tonic_candidate * (2 ** (2. / 53))):
                    tonic = {"estimated_tonic": tonic_candidate,
                             "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                    break  #  tonic found

                elif last_note >= tonic_candidate or last_note <= tonic_candidate:
                    if last_note <= tonic_candidate:
                        times = round(tonic_candidate / last_note)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note * times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            tonic = {"estimated_tonic": tonic_candidate,
                                     "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                            break  #  tonic found

                    else:
                        times = round(last_note / tonic_candidate)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note / times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            tonic = {"estimated_tonic": tonic_candidate,
                                     "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                            break  #  tonic found
            cnt += 1

        # octave correction
        temp_tonic = tonic['estimated_tonic'] / 2
        temp_candidate = self.find_nearest(stable_pitches, temp_tonic)

        closest_temp_cand = self.find_nearest(peaks[0], temp_candidate)
        temp_candidate_ind = [i for i, x in enumerate(peaks[0]) if x == closest_temp_cand]
        temp_candidate_occurrence = peaks[1][temp_candidate_ind[0]]

        closest_peak = self.find_nearest(peaks[0], tonic['estimated_tonic'])
        tonic_ind = [i for i, x in enumerate(peaks[0]) if x == closest_peak]
        tonic_occurrence = peaks[1][tonic_ind[0]]

        if (temp_candidate / (2 ** (1. / 53))) <= temp_tonic <= (temp_candidate * (2 ** (1. / 53))):
            if tonic['estimated_tonic'] >= 400:
                if verbose:
                    print "OCTAVE CORRECTED!!!!"
                octave_wrapped = 0
                tonic = {"estimated_tonic": temp_candidate,
                         "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}

            if tonic_occurrence <= temp_candidate_occurrence:
                if verbose:
                    print "OCTAVE CORRECTED!!!!"
                octave_wrapped = 0
                tonic = {"estimated_tonic": temp_candidate,
                         "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}

        else:
            if verbose:
                print "No octave correction!!!"
            octave_wrapped = 1

        return_tonic = {
                        "value": tonic['estimated_tonic'],
                        "unit": "Hz",
                        "timeInterval": {"value":tonic['time_interval'], "unit":'sec'},
                        "timeUnit": "sec",
                        "octaveWrapped": octave_wrapped,
                        "procedure": "Tonic identification by detecting the last note",
                        "reference": 'Atlı, H. S., Bozkurt, B., Şentürk, S. (2015). ' 
                                     'A Method for Tonic Frequency Identification of ' 
                                     'Turkish Makam Music Recordings. In Proceedings of '
                                     '5th International Workshop on Folk Music Analysis, '
                                     'pages 119–122, Paris, France.'
                        }

        if plot:
            self.plot(pitch, return_tonic, pitch_chunks, distribution)

        if verbose:
            print last_note
            print tonic
            print sorted(stable_pitches)

        return return_tonic, pitch, pitch_chunks, distribution, stable_pitches

    def plot(self, pitch, tonic, pitch_chunks, distribution):
        fig, (ax1, ax2, ax3) = plt.subplots(3, num=None, figsize=(18, 8), dpi=80)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.4)

        # plot title
        ax1.set_title('Pitch Distribution')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Frequency of occurrence')

        # log scaling the x axis
        ax1.set_xscale('log', basex=2, nonposx='clip')
        ax1.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))

        # recording distribution
        ax1.plot(distribution.bins, distribution.vals, label='SongHist', ls='-', c='b', lw='1.5')

        # peaks
        peaks = distribution.detect_peaks()
        ax1.plot(distribution.bins[peaks[0]], peaks[1], 'cD', ms=6, c='r')

        # tonic
        ax1.plot(tonic['value'],
                 distribution.vals[where(distribution.bins == tonic['value'])[0]], 'cD', ms=10)

        # pitch distributiongram
        ax2.plot([element[0] for element in pitch], [element[1] for element in pitch], ls='-', c='r', lw='0.8')
        ax2.vlines([element[0][0] for element in pitch_chunks], 0,
                   max([element[1]] for element in pitch))
        ax2.set_xlabel('Time (secs)')
        ax2.set_ylabel('Frequency (Hz)')

        ax3.plot([element[0] for element in pitch_chunks[-1]],
                 [element[1] for element in pitch_chunks[-1]])
        ax3.set_title("Last Chunk")
        ax3.set_xlabel('Time (secs)')
        ax3.set_ylabel('Frequency (Hz)')
        plt.show()
