import numpy as np
from scipy.io import wavfile
import argparse
import random

SAMPLE_RATE = 48000
AMPLITUDE = 0.3
DTYPE = np.int16

SONG_STRUCTURES = ["AABB/CC", "ABAB/CD", "AB/CDDD"]

CHORD_LOOPS = [
    (1, 4, 2, 5),
    (1, 6, 2, 5),
    (1, 3, 4, 4),
    (1, 5, 2, 5),
    (1, 6, 4, 5),
    (4, 1, 6, 4),
    (1, 5, 6, 1),
    (1, 4, 4, 1),
    (4, 5, 1, 1),
    (6, 4, 1, 5),
]

IV_MINOR_LOOPS = {2: {3}, 7: {2}}
MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

TRIAD_SEMITONES = {
    1: (0,  4,  7),
    2: (2,  5,  9),
    3: (4,  7, 11),
    4: (5,  9, 12),
    5: (7, 11, 14),
    6: (9, 12, 16),
}

IV_MINOR_SEMITONES = (5, 8, 12)

NOTE_NAMES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

def midi_freq(midi_note):
    """
    This function converts a MIDI note number to a frequency in Hz.
    """
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def midi_key(key_index, octave):
    """
    This function returns the MIDI note for a key index value (0=A, 1=A#, …, 11=G#) for a given octave.
    """
    return 57 + key_index + (octave - 3) * 12

def midi_scale(key_midi_root):
    """
    This function returns all MIDI note values in the octave of the major scale
    starting at key_midi_root.
    """
    return [key_midi_root + interval for interval in MAJOR_SCALE_INTERVALS]

def midi_chord(key_midi_root, degree, loop_idx, position):
    """
    This function returns the MIDI notes of a major chord.
    It also handles the iv minor case using IV_MINOR_LOOPS.
    """
    is_iv_minor = (loop_idx in IV_MINOR_LOOPS) and (position in IV_MINOR_LOOPS[loop_idx])
    if is_iv_minor:
        semitones = IV_MINOR_SEMITONES
    else:
        semitones = TRIAD_SEMITONES[degree]
    return [key_midi_root + s for s in semitones]

def parse_structure(structure_str):
    """
    This function parses a song structure like "AABB/CC" into a list of chars.
    """
    return [ch for ch in structure_str if ch.isalpha()]

def make_labels(structure_str):
    """
    This function returns the set of unique line labels in a structure string.
    """
    return sorted(set(ch for ch in structure_str if ch.isalpha()))

def assign_loops(labels):
    """
    This function randomly assigns a chord loop from CHORD_LOOPS to each unique label.
    """
    chosen_indices = random.sample(range(len(CHORD_LOOPS)), len(labels))
    return {label: (idx, CHORD_LOOPS[idx]) for label, idx in zip(labels, chosen_indices)}

def sawtooth_wave(freq, duration_samples):
    """
    This function generates a mono sawtooth wave at the given frequency.
    """
    t = np.arange(duration_samples) / SAMPLE_RATE
    phase = t * freq
    return 2.0 * (phase - np.floor(phase + 0.5))

def note_sound(midi_note, duration_samples):
    """
    This function renders a note as a sawtooth wave with a simple amplitude.
    """
    wave = sawtooth_wave(midi_freq(midi_note), duration_samples)
    env = np.ones(duration_samples)
    attack = min(int(SAMPLE_RATE * 0.01), duration_samples)
    release = min(int(SAMPLE_RATE * 0.05), duration_samples)
    env[:attack]  = np.linspace(0.0, 1.0, attack)
    env[-release:] = np.linspace(1.0, 0.0, release)
    return wave * env

def melody(chord_midis, scale_midis):
    """
    This function picks a melody note: chord tone with probability 0.8, scale tone otherwise.
    """
    if random.random() < 0.8:
        return random.choice(chord_midis)
    return random.choice(scale_midis)

def four_chord_audio(loop_idx, loop, key_root_midi, samples_per_eighth):
    """
    This function generates audio samples for one song line (4 chord loop, 8 eighth notes per measure).
    """
    scale_midis = midi_scale(key_root_midi)
    audio_chunks = []

    for pos, degree in enumerate(loop):
        chord_midis = midi_chord(key_root_midi, degree, loop_idx, pos)
        for _ in range(8):
            note = melody(chord_midis, scale_midis)
            chunk = note_sound(note, samples_per_eighth)
            audio_chunks.append(chunk)

    return np.concatenate(audio_chunks)

def build_song(structure_str, label_to_loop, key_root_midi, bpm):
    """
    This function builds the full song as an audio array.
    """
    beats_per_minute  = bpm
    seconds_per_beat  = 60.0 / beats_per_minute
    seconds_per_eighth = seconds_per_beat / 2.0
    samples_per_eighth = int(SAMPLE_RATE * seconds_per_eighth)

    line_audio = {}
    for label, (loop_idx, loop) in label_to_loop.items():
        line_audio[label] = four_chord_audio(loop_idx, loop, key_root_midi, samples_per_eighth)

    line_sequence = parse_structure(structure_str)
    song_chunks = [line_audio[label] for label in line_sequence]
    return np.concatenate(song_chunks)

def float_to_int16(audio):
    """
    This function clips and convert a float64 audio array to int16 PCM samples.
    """
    clipped = np.clip(audio * AMPLITUDE, -1.0, 1.0)
    return (clipped * 32767).astype(DTYPE)

def main():
    parser = argparse.ArgumentParser(description="Music maker!")
    parser.add_argument("--output", metavar="FILENAME.wav",
                        help="Saves audio to output file instead of playing.")
    args = parser.parse_args()

    song_structure = random.choice(SONG_STRUCTURES)
    bpm = random.randint(80, 160)
    key = random.randint(0, 11)
    octave = random.randint(3, 4)
    midi_root = midi_key(key, octave)

    labels        = make_labels(song_structure)
    label_to_loop = assign_loops(labels)

    print(f"Structure : {song_structure}")
    print(f"Key : {NOTE_NAMES[key]}{octave}")
    print(f"Tempo : {bpm} BPM")
    for label, (loop_idx, loop) in sorted(label_to_loop.items()):
        degree_names = {1:"I",2:"ii",3:"iii",4:"IV",5:"V",6:"vi"}
        loop_str = "-".join(degree_names[d] for d in loop)
        print(f"Line {label} : {loop_str}")

    song_float = build_song(song_structure, label_to_loop, midi_root, bpm)
    song_int16 = float_to_int16(song_float)

    if args.output:
        wavfile.write(args.output, SAMPLE_RATE, song_int16)
        print(f"Written   : {args.output}")
    else:
        try:
            import sounddevice as sd
            sd.play(song_int16.astype(np.float32) / 32767.0, SAMPLE_RATE)
            sd.wait()
        except ImportError:
            print("sounddevice not installed")

if __name__ == "__main__":
    main()