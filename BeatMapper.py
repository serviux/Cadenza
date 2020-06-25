from essentia.standard import *
import json
# Loading audio file
audio = MonoLoader(filename=r'music/TurnipKnightRun.wav')()



# Compute beat positions and BPM
rhythm_extractor = RhythmExtractor2013(method="multifeature")
bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

song_info = {
    "Title": "Turnip Knight Run",
    "Artist": "Josh Cormier",
    "BPM": bpm,
    "Beats": list(beats),
    "Confidence": beats_confidence,
    "Beat_Intervals": list(beats_intervals)
}

print(song_info)


# Mark beat positions on the audio and write it to a file
# Let's use beeps instead of white noise to mark them, as it's more distinctive
marker = AudioOnsetsMarker(onsets=beats, type='beep')
marked_audio = marker(audio)
MonoWriter(filename='music/Flight_marked.mp3')(marked_audio)
