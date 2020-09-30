"""This tools pulls the data analyzed from the music_data_manager and creates
an beatmap for the given song"""


import pandas as pd
from statistics import median
from random import randint
from decimal import Decimal




class MapMaker:

    def __init__(self):
        self.beats = []
        self.hfc = []
        self.complex = []
        self.bpm = 0
        self.measures = []
        self.total_onsets = []


    def do_work(self):
        """Performs most of the work for the class"""
        measure = []
        first_time = True
        for i, beat in enumerate(self.beats):
            if i % 4 == 0 and not first_time:
                self.measures.append(measure)
                measure = []
            measure.append(beat)
            first_time = False

        for m in self.measures:
            measure_details = self._calculate_measure_fitness(m)
            crossover = self.measure_crossover(measure_details)
            self.total_onsets.extend(crossover)


    def _calculate_measure_fitness(self, measure):
        """Calculates how accurate a measure is and returns a dict with information about it
        dict is like:
        {
            measure_start,
            measure_end,
            hfc_onsets,
            complex_onsets,
            hfc_onset_deltas,
            complex_onset_deltas,
            min_delta_complex
            min_delta_hfc
            max_delta_complex
            max_delta_hfc
            med_delta_complex
            med_delta_hfc
            fitness
        }
        Parameters
        ----------
            measure: list<float>
                list of beats in the measure"""
        beat_length = (self.bpm / 60)

        start = measure[0]
        end = measure[3] + beat_length

        # find all the onsets for a given measure from the hfc  complex dataframes
        hfc_onsets = self.hfc[(self.hfc["float_onsets"] <= end) & (self.hfc["float_onsets"] >= start)]
        complex_onsets = self.complex[(self.complex["float_onsets"] <= end) & (self.complex["float_onsets"] >= start)]

        hfc_onset_deltas = []
        complex_onsets_deltas = []

        # find the difference between all the onsets in a measure for both complex and hfc

        prev_onset = hfc_onsets.iloc[0]["float_onsets"]
        for onset in hfc_onsets["float_onsets"][1:]:
            odt = self._calculate_onset_delta(prev_onset, onset)
            hfc_onset_deltas.append(odt)
            prev_onset = onset

        prev_onset = complex_onsets.iloc[0]["float_onsets"]
        for onset in complex_onsets["float_onsets"][1:]:
            odt = self._calculate_onset_delta(prev_onset, onset)
            complex_onsets_deltas.append(odt)
            prev_onset = onset

        hfc_avg = sum(hfc_onset_deltas)/len(hfc_onset_deltas)
        complex_avg = sum(complex_onsets_deltas)/len(complex_onsets_deltas)
        max_hfc = max(hfc_onset_deltas)
        max_complex = max(complex_onsets_deltas)
        min_hfc = min(hfc_onset_deltas)
        min_complex = min(complex_onsets_deltas)
        med_hfc = median(hfc_onset_deltas)
        med_complex = median(complex_onsets_deltas)

        """
        For calculating fitness there are several steps
            everything starts a base score 100
            
            step 1:  100 * avg
            step 2:  (100 * avg)/(max*10)
            step 3:  ((100 * avg)/(max*10)) * (1/min)  
            step 4:  ((100 * avg)/(max*10)) * (1/min) * med
            
            the biggest factor is the max delta onset, becuase we don't want to leave large gaps 
            in the beatmap, because it's not as much fun to play, but it's ok to be able some gaps.
            however, it will be considered weaker based off the larger space.
        """
        complex_fitness = ((100 * complex_avg)/(max_complex*10)) * (1/min_complex) * med_complex
        hfc_fitness = ((100 * hfc_avg)/(max_hfc*10)) * (1/min_hfc) * med_hfc

        return{
            "start": start,
            "stop": end,
            "hfc_onsets": hfc_onsets,
            "complex_onsets": complex_onsets,
            "hfc_onset_deltas": hfc_onset_deltas,
            "complex_onset_deltas": complex_onsets_deltas,
            "min_delta_complex": min_complex,
            "min_delta_hfc": min_hfc,
            "avg_delta_complex": complex_avg,
            "avg_delta_hfc": hfc_avg,
            "max_delta_complex": max_complex,
            "max_delta_hfc": max_hfc,
            "med_delta_hfc": med_hfc,
            "med_delta_complex": med_complex,
            "fitness_hfc": hfc_fitness,
            "fitness_complex": complex_fitness
        }


    def _calculate_onset_delta(self, onset1, onset2):
        """finds how much time has passed between onset1 and onset2
        Parameters
        ----------
            onset1: float
                time of onset in the music
            onset2: float
                time onset in the music"""
        if onset2 < onset1:
            raise FloatingPointError("onset2 cannot be less than onset1")
        return onset2 - onset1


    def measure_crossover(self, measure_dict):
        """mutates both the measures into one semi-randomly
        Parameters
        ----------
        both dicts just need to have the fitness and the onsets out of the calcuation
        measure_dict1: dict
            first measure to be merged
     """

        onsets_hfc = measure_dict["hfc_onsets"]
        onsets_complex = measure_dict["complex_onsets"]


        # what is the smallest reasonable time for two notes to be together
        # ex.)
        #      100 beats           1min
        #      --------    x     ---------   =    1.666 beats per second
        #        1 min             60sec
        #
        #
        #     1.66beats          1/16 64th notes
        #     ---------   x     ----------------   = 0.10375 64th per second
        #      1 sec               1 beat

        
        hfc_center = int(len(onsets_hfc)/2)
        comp_center = int(len(onsets_complex)/2)


        r = (randint(0, 1) == 1)
        combined_measure = []
        if r:
            lower_half = onsets_hfc["float_onsets"][hfc_center::-1]
            lower_half = lower_half.tolist()
            lower_half.reverse()
            upper_half = onsets_complex[comp_center+1:]
            combined_measure.extend(lower_half)
            combined_measure.extend(upper_half)
        else:
            lower_half = onsets_complex["float_onsets"][comp_center::-1]
            lower_half = lower_half.tolist()
            lower_half.reverse()
            upper_half = onsets_hfc[hfc_center + 1:]
            combined_measure.extend(lower_half)
            combined_measure.extend(upper_half)

        return combined_measure

def main():
    title = "Konga Conga Kappa"
    artist = "Danny Baranowsky"
    mm = MapMaker()
    mm.do_work()

        
if __name__ == "__main__":
    main()
