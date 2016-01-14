# -*- coding: utf-8 -*-
__author__ = 'hsercanatli'

from numpy import median
from numpy import where
from histogram import Histogram

import matplotlib.pyplot as plt
import matplotlib.ticker

class TonicLastNote:
    def __init__(self):
        self.stable_pitches = []
        self.time_interval = None

    @staticmethod
    def find_nearest(array, value):
        distance = [abs(element - value) for element in array]
        idx = distance.index(min(distance))
        return array[idx]

    def identify(self, pitch, plot=False, verbose=False):
        """
        plot function
        """
        tonic = 0
        octave_wrapped = 1

        # getting histograms 3 times more resolution
        histo = Histogram(times=3)
        pitch_chunks, normal_histo = histo.compute(pitch)

        self.stable_pitches = histo.peaks["peaks"][0]

        cnt = 1
        while tonic is 0:
            last_chunk = [element[1] for element in pitch_chunks[-cnt]]

            last_note = median(last_chunk)
            self.stable_pitches = sorted(self.stable_pitches, key=lambda x: abs(last_note - x))

            for j in range(len(self.stable_pitches)):
                tonic_candidate = float(self.stable_pitches[j])

                if (tonic_candidate / (2 ** (2. / 53))) <= last_note <= (tonic_candidate * (2 ** (2. / 53))):
                    tonic = {"estimated_tonic": tonic_candidate,
                             "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                    print "Tonic=", tonic
                    break

                elif last_note >= tonic_candidate or last_note <= tonic_candidate:
                    if last_note <= tonic_candidate:
                        times = round(tonic_candidate / last_note)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note * times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            tonic = {"estimated_tonic": tonic_candidate,
                                     "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                            print "Tonic=", tonic
                            break

                    else:
                        times = round(last_note / tonic_candidate)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note / times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            tonic = {"estimated_tonic": tonic_candidate,
                                     "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}
                            print "Tonic=", tonic
                            break
            cnt += 1

        # octave correction
        temp_tonic = tonic['estimated_tonic'] / 2
        temp_candidate = self.find_nearest(self.stable_pitches, temp_tonic)
        temp_candidate_ind = [i for i, x in enumerate(histo.peaks['peaks'][0]) if x == temp_candidate]
        temp_candidate_occurrence = histo.peaks["peaks"][1][temp_candidate_ind[0]]

        tonic_ind = [i for i, x in enumerate(histo.peaks['peaks'][0]) if x == tonic['estimated_tonic']]
        tonic_occurrence = histo.peaks["peaks"][1][tonic_ind[0]]

        if (temp_candidate / (2 ** (1. / 53))) <= temp_tonic <= (temp_candidate * (2 ** (1. / 53))):
            if tonic['estimated_tonic'] >= 400:
                print "OCTAVE CORRECTED!!!!"
                octave_wrapped = 0
                tonic = {"estimated_tonic": temp_candidate,
                         "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}

            if tonic_occurrence <= temp_candidate_occurrence:
                print "OCTAVE CORRECTED!!!!"
                octave_wrapped = 0
                tonic = {"estimated_tonic": temp_candidate,
                         "time_interval": [pitch_chunks[-cnt][0][0], pitch_chunks[-cnt][-1][0]]}

        else:
            print "No octave correction!!!"
            octave_wrapped = 1

        if plot:
            self.plot(pitch, tonic, pitch_chunks, histo)

        if verbose:
            print last_note
            print tonic
            print sorted(self.stable_pitches)

        return_tonic = {
                        "value": tonic['estimated_tonic'],
                        "unit": "Hz",
                        "timeInterval": {"value":tonic['time_interval'], "unit":'sec'},
                        "timeUnit": "sec",
                        "octaveWrapped": octave_wrapped,
                        "procedure": "Tonic identification by detecting the last note",
                        "reference": "Atlı, H. S., Bozkurt, B., Şentürk, S. (2015). A Method for Tonic Frequency Identification of Turkish Makam Music Recordings. In Proceedings of 5th International Workshop on Folk Music Analysis, pages 119–122, Paris, France."
                        }

        return return_tonic, pitch, pitch_chunks, histo

    def plot(self, pitch, tonic, pitch_chunks, histo):
        fig, (ax1, ax2, ax3) = plt.subplots(3, num=None, figsize=(18, 8), dpi=80)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.4)

        # plot title
        ax1.set_title('Recording Histogram')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Frequency of occurrence')
        # log scaling the x axis
        ax1.set_xscale('log', basex=2, nonposx='clip')
        ax1.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
        # recording histogram
        ax1.plot(histo.x, histo.y, label='SongHist', ls='-', c='b', lw='1.5')
        # peaks
        ax1.plot(histo.peaks['peaks'][0], histo.peaks['peaks'][1], 'cD', ms=6, c='r')
        # tonic
        ax1.plot(tonic['estimated_tonic'],
                 histo.y[where(histo.x == tonic['estimated_tonic'])[0]], 'cD', ms=10)

        # pitch histogram
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
