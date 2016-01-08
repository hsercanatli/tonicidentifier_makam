from numpy import delete
from numpy import log2
from numpy import arange
from numpy import histogram

class Histogram(object):
    def __init__(self, post_filter=True, freq_limit=False, 
        bottom_limit=64, upper_limit=1024):
        
        # inputs
        self.post_filter = post_filter
        self.freq_limit = freq_limit
        self.bottom_limit = bottom_limit
        self.upper_limit = upper_limit

        # outputs
        self.normal_histogram = {}

    @staticmethod
    def energy_filter(pitch, threshold=0.002):
        """
        checks the saliences
        """
        for element in pitch:
            if element[2] <= threshold and element[1] != 0:
                element[1] = 0
                element[2] = 0

        return pitch

    def decompose_into_chunks(self, pitch, bottom_limit=0.8, upper_limit=1.2):
        """
        decomposes the given pitch track into the chunks.
        """
        pitch_chunks = []
        temp_pitch = [pitch[0]]

        # starts at the first sample
        for i in range(1, len(pitch) - 1):
            # separation of the zero chunks
            if pitch[i][1] == 0:
                if pitch[i + 1][1] == 0:
                    temp_pitch.append(pitch[i + 1])

                else:
                    temp_pitch.append(pitch[i])
                    pitch_chunks.append(temp_pitch)
                    temp_pitch = []
            # non-zero chunks
            else:
                interval = float(pitch[i + 1][1]) / float(pitch[i][1])
                if bottom_limit < interval < upper_limit:
                    temp_pitch.append(pitch[i])
                else:
                    temp_pitch.append(pitch[i])
                    pitch_chunks.append(temp_pitch)
                    temp_pitch = []
        pitch_chunks.append(temp_pitch)

        if self.post_filter:
            return self.post_filter_chunks(pitch_chunks, chunk_limit=60, freq_limit=self.freq_limit)
        else:
            return pitch_chunks

    def post_filter_chunks(self, pitch_chunks, chunk_limit=60, freq_limit=True):
        """
        Postfilter for the pitchChunks
        deletes the zero chunks
        deletes the chunks smaller than 60 samples(default)
        """
        # deleting Zero chunks
        zero_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] == 0]
        pitch_chunks = delete(pitch_chunks, zero_chunks)

        # deleting small Chunks
        small_chunks = [i for i in range(0, len(pitch_chunks)) if len(pitch_chunks[i]) <= chunk_limit]
        pitch_chunks = delete(pitch_chunks, small_chunks)

        # frequency limit
        if freq_limit:
            limit_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] >= self.upper_limit or
                            pitch_chunks[i][0][1] <= self.bottom_limit]
            pitch_chunks = delete(pitch_chunks, limit_chunks)

        return pitch_chunks

    @staticmethod
    def recompose_chunks(pitch_chunks):
        """
        recomposes the given pitch chunks as a new pitch track
        """
        return [pitch_chunks[i][j] for i in range(len(pitch_chunks))
                      for j in range(len(pitch_chunks[i]))]

    def compute(self, pitch, times=1):
        """
        Computes the histogram for given pitch track
        """
        pitch = self.energy_filter(pitch)

        pitch_chunks = self.decompose_into_chunks(pitch)
        pitch = self.recompose_chunks(pitch_chunks)

        pitch_chunks = self.decompose_into_chunks(pitch, bottom_limit=0.965, upper_limit=1.035)
        pitch = self.recompose_chunks(pitch_chunks)

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
        step_no = 4 * 53 * 3 * times
        edges = (arange(step_no + 1) * (1. / (3 * times * 53.))) + min_logf0
        # pitch histogram
        hist = histogram(log_pitch, edges)[0]
        # normalization of the histogram
        hist = [float(hist[i]) / sum(hist) for i in range(len(hist))]
        # edges calculation
        edges = [2 ** ((edges[i] + edges[i + 1]) / 2.) for i in range(len(edges) - 1)]

        self.normal_histogram = {'bins': edges, 'hist': hist}
        return pitch_chunks
