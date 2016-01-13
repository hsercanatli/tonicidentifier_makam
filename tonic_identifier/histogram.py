from numpy import delete
from numpy import log2
from numpy import arange
from numpy import histogram

from pypeaks import Data
from pitchfilter.pitchfilter import PitchPostFilter

class Histogram(Data):
    def __init__(self, times=1, bottom_freq_limit=64, upper_freq_limit=1024,
                 chunk_limit=60, bottom_limit=0.965, upper_limit=1.035):

        # inputs
        self.times = times
        self.bottom_freq_limit = bottom_freq_limit
        self.upper_freq_limit = upper_freq_limit
        self.chunk_limit = chunk_limit
        self.bottom_limit = bottom_limit
        self.upper_limit = upper_limit

    def post_filter_chunks(self, pitch_chunks):
        """
        Postfilter for the pitchChunks
        deletes the zero chunks
        deletes the chunks smaller than 60 samples(default)
        """
        # deleting Zero chunks
        zero_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] == 0]
        pitch_chunks = delete(pitch_chunks, zero_chunks)

        # deleting small Chunks
        small_chunks = [i for i in range(0, len(pitch_chunks)) if len(pitch_chunks[i]) <= self.chunk_limit]
        pitch_chunks = delete(pitch_chunks, small_chunks)

        # frequency limit
        limit_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] >= self.upper_freq_limit or
                        pitch_chunks[i][0][1] <= self.bottom_freq_limit]
        pitch_chunks = delete(pitch_chunks, limit_chunks)

        return pitch_chunks

    def compute(self, pitch):
        """
        Computes the histogram for given pitch track
        """
        flt = PitchPostFilter()
        pitch_chunks = flt.decompose_into_chunks(pitch)
        pitch_chunks = self.post_filter_chunks(pitch_chunks)

        pitch = flt.recompose_chunks(pitch_chunks)

        pitch = [sample[1] for sample in pitch]

        # log2 of pitch track
        log_pitch = log2(pitch)

        # calculating the bins in 4 octave range...
        max_logf0 = max(log_pitch)
        if max_logf0 > 5:
            min_logf0 = max_logf0 - 4.
        else:
            print '!!!PROBLEM!!!\nCheck the given audio recording. Range is lower than 4 octave'

        # 1/3 holderian comma in 4 octave
        step_no = 4 * 53 * 3 * self.times
        edges = (arange(step_no + 1) * (1. / (3 * self.times * 53.))) + min_logf0

        # pitch histogram
        hist = histogram(log_pitch, edges)[0]

        # normalize the histogram
        hist = [float(hist[i]) / sum(hist) for i in range(len(hist))]

        # edge calculation
        edges = [2 ** ((edges[i] + edges[i + 1]) / 2.) for i in range(len(edges) - 1)]
        normal_histogram = {'x': edges, 'y': hist}

        # get histogram peaks with pypeaks library
        Data.__init__(self, normal_histogram['x'], normal_histogram['y'], smoothness=3)
        self.get_peaks(method='slope')

        return pitch_chunks, normal_histogram
