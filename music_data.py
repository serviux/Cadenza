from essentia.standard import *
from pylab import plot, show, figure, imshow
from decimal import Decimal
import matplotlib.pyplot as plt
import os.path
import json
import pandas as pd

class MusicData:
    """Finds the onsets and beats for a given song"""
    def __init__(self, file_path,  title="", artist=""):
        self.Title = title
        self.Artist = artist
        self.BPM = 0
        self.beat_confidence = 0
        self.beats = []
        self.beat_intervals = []
        self.audio = None
        self.onsets_complex = []
        self.onsets_hfc = []
        self.file_path = file_path
        self.format = os.path.splitext(self.file_path)[1][1:]
        self.audio = MonoLoader(filename=self.file_path)()


    def detect_beats(self):
        """attemps to find beats for a given song"""
        rhythm_extractor = RhythmExtractor2013(method="multifeature")
        bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(self.audio)
        self.BPM = bpm
        self.beats = beats
        self.beat_confidence = beats_confidence
        self.beat_intervals = beats_intervals


    def save_beat_diagram(self):
        """Saves the diagram of detected beats in a song"""
        plot(self.audio)
        for beat in self.beats:
            plt.axvline(x=beat*44100, color='red')

        plt.title("Audio waveform and the estimated beat positions")
        plt.savefig("audio_data/beats.png")


    def save_onsets_diagram(self):
        """Saves a diagram of the detected onsets from hfc and complex"""
        
        plot(self.audio)
        for onset in self.onsets_hfc:
            plt.axvline(x=onset*44100, color='red')

        plt.title("Audio waveform and the estimated onset positions (HFC onset detection function)")
        plt.savefig("audio_data/hfc.png")

        plot(self.audio)
        for onset in self.onsets_complex:
            plt.axvline(x=onset*44100, color='red')

        plt.title("Audio waveform and the estimated onset positions (Complex onset detection function)")
        plt.savefig("audio_data/complex.png")


    def detect_onsets(self):
        """detects the onsets using hfc and complex methods"""
        od1 = OnsetDetection(method='hfc')
        od2 = OnsetDetection(method='complex')

        # Let's also get the other algorithms we will need, and a pool to store the results
        w = Windowing(type='hann')
        fft = FFT()  # this gives us a complex FFT
        c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
        pool = essentia.Pool()

        # Computing onset detection functions.
        for frame in FrameGenerator(self.audio, frameSize=1024, hopSize=512):
            mag, phase, = c2p(fft(w(frame)))
            pool.add('features.hfc', od1(mag, phase))
            pool.add('features.complex', od2(mag, phase))

        # Phase 2: compute the actual onsets locations
        onsets = Onsets()

        onsets_hfc = onsets(  # this algo expects a matrix, not a vector
            essentia.array([pool['features.hfc']]),

            # you need to specify weights, but as there is only a single
            # function, it doesn't actually matter which weight you give it
            [1])
        onsets_complex = onsets(essentia.array([pool['features.complex']]), [1])
        
        silence = [0.] * len(self.audio)
        self.onsets_hfc = onsets_hfc
        self.onsets_complex = onsets_complex
        beeps_hfc = AudioOnsetsMarker(onsets=onsets_hfc, type='beep')(silence)
        AudioWriter(filename=f'audio_data/hfc.{self.format}',
                    format=self.format)(StereoMuxer()(self.audio, beeps_hfc))

        beeps_complex = AudioOnsetsMarker(onsets=onsets_complex,
                                          type='beep')(silence)
        AudioWriter(filename=f'audio_data/complex.{self.format}', 
                    format=self.format)(StereoMuxer()(self.audio, beeps_complex))


    def to_dict(self):
        """Returns a dict object of all info the in the class"""
        return self.__class__.__dict__