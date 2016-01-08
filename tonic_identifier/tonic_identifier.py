# -*- coding: utf-8 -*-
__author__ = 'hsercanatli'

from numpy import median
from numpy import where

from histogram import Histogram

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

class TonicLastNote():
    def __init__(self):
        self.pitch = []
        self.pitch_chunks = [[]]
        self.tonic = 0
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
        self.pitch = pitch

        # getting histograms 3 times more resolution
        histo = Histogram(post_filter=True, freq_limit=True, bottom_limit=64, upper_limit=1024)
        self.pitch_chunks = histo.compute(pitch, times=3)

        self.peaks_list = histo.peaks["peaks"][0]

        cnt = 1
        while self.tonic is 0:
            last_chunk = [element[1] for element in self.pitch_chunks[-cnt]]

            last_note = median(last_chunk)
            self.peaks_list = sorted(self.peaks_list, key=lambda x: abs(last_note - x))

            for j in range(len(self.peaks_list)):
                tonic_candidate = float(self.peaks_list[j])

                if (tonic_candidate / (2 ** (2. / 53))) <= last_note <= (tonic_candidate * (2 ** (2. / 53))):
                    self.tonic = {"estimated_tonic": tonic_candidate,
                                  "time_interval": [self.pitch_chunks[-cnt][0][0],
                                                    self.pitch_chunks[-cnt][-1][0]]}
                    print "Tonic=", self.tonic
                    break

                elif last_note >= tonic_candidate or last_note <= tonic_candidate:
                    if last_note <= tonic_candidate:
                        times = round(tonic_candidate / last_note)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note * times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            self.tonic = {"estimated_tonic": tonic_candidate,
                                          "time_interval": [self.pitch_chunks[-cnt][0][0],
                                                            self.pitch_chunks[-cnt][-1][0]]}
                            print "Tonic=", self.tonic
                            break

                    else:
                        times = round(last_note / tonic_candidate)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note / times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            self.tonic = {"estimated_tonic": tonic_candidate,
                                          "time_interval": [self.pitch_chunks[-cnt][0][0],
                                                            self.pitch_chunks[-cnt][-1][0]]}
                            print "Tonic=", self.tonic
                            break
            cnt += 1

        # octave correction
        temp_tonic = self.tonic['estimated_tonic'] / 2
        temp_candidate = self.find_nearest(self.peaks_list, temp_tonic)
        temp_candidate_ind = [i for i, x in enumerate(histo.peaks['peaks'][0]) if x == temp_candidate]
        temp_candidate_occurence = histo.peaks["peaks"][1][temp_candidate_ind[0]]

        tonic_ind = [i for i, x in enumerate(histo.peaks['peaks'][0]) if x == self.tonic['estimated_tonic']]
        tonic_occurrence = histo.peaks["peaks"][1][tonic_ind[0]]

        if (temp_candidate / (2 ** (1. / 53))) <= temp_tonic <= (temp_candidate * (2 ** (1. / 53))):
            if self.tonic['estimated_tonic'] >= 400:
                print "OCTAVE CORRECTED!!!!"
                self.tonic = {"estimated_tonic": temp_candidate,
                              "time_interval": [self.pitch_chunks[-cnt][0][0],
                                                self.pitch_chunks[-cnt][-1][0]]}

            if tonic_occurrence <= temp_candidate_occurence:
                print "OCTAVE CORRECTED!!!!"

                self.tonic = {"estimated_tonic": temp_candidate,
                              "time_interval": [self.pitch_chunks[-cnt][0][0],
                                                self.pitch_chunks[-cnt][-1][0]]}
                print self.tonic
        else: print "No octave correction!!!"

        if plot:
            self.plot_tonic()
            plt.show()

        if verbose:
            print last_note
            print self.tonic
            print sorted(self.peaks_list)

        return self.tonic

    def plot_tonic(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, num=None, figsize=(18, 8), dpi=80)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.4)

        # plot title
        ax1.set_title('Recording Histogram')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Frequency of occurrence')
        # log scaling the x axis
        ax1.set_xscale('log', basex=2, nonposx='clip')
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        # recording histogram
        ax1.plot(self.x, self.y, label='SongHist', ls='-', c='b', lw='1.5')
        # peaks
        ax1.plot(self.peaks['peaks'][0], self.peaks['peaks'][1], 'cD', ms=6, c='r')
        # tonic
        ax1.plot(self.tonic['estimated_tonic'],
                 self.y[where(self.x == self.tonic['estimated_tonic'])[0]], 'cD', ms=10)

        # pitch track histogram
        ax2.plot([element[0] for element in self.pitch], [element[1] for element in self.pitch], ls='-', c='r', lw='0.8')
        ax2.vlines([element[0][0] for element in self.pitch_chunks], 0,
                   max([element[1]] for element in self.pitch))
        ax2.set_xlabel('Time (secs)')
        ax2.set_ylabel('Frequency (Hz)')

        ax3.plot([element[0] for element in self.pitch_chunks[-1]],
                 [element[1] for element in self.pitch_chunks[-1]])
        ax3.set_title("Last Chunk")
        ax3.set_xlabel('Time (secs)')
        ax3.set_ylabel('Frequency (Hz)')
        plt.show()
