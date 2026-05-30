# Aleatoric Music Generator

## Sawyer King

### Overview:

This project implements an aleatoric music generator. The program randomly selects a song structure, key, tempo, and chord loops. Then it makes the audio using sawtooth waves. The output is either played through the users speakers or output to a .wav file if --output FILENAME.wav is provided.

## What I did:

- I ensured that the program randomly selects song structures from provided list of structures: "AABB/CC", "ABAB/CD", or "AB/CDDD"
- I assigned a four chord loop to each line while ensuring no two labels share the same loop.
- I have the program pick a random key and tempo.
- I generate each note as a sawtooth wav form.
- I added functionality for saving the audio to a .wav file.

## How it went:

The implementation went smoothly overall. Structuring the codebase around small functions made it straightforward to build and test each layer independently. I would say that one of the more challenging parts was messing around with scales and semitones with midi integration as I don't have too much musical experience so I was learning many things in parallel.

## What still needs to be done:

- All optional features: bass, drums, harmony, rhythm, percussion, etc
- Error handling
- Unit testing would probably be good
