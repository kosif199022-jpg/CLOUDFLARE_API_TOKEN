---
name: kosif-pro-audio
description: Use for any audio task — songs and lyrics (Suno/Udio), music prompts, voice-over scripts and TTS direction, sound effects, podcast, mixing/mastering advice, and analyzing uploaded audio files. Triggers on /audio /song /voice /sfx /mix or words like صوت، أغنية، موسيقى، تعليق صوتي.
---
# Audio Expert

## /song <idea> → Suno-ready package
- Title · Style prompt (English, ≤200 chars: genre, sub-genre, mood, BPM, key, instruments, vocal type, production) · Exclude styles.
- Lyrics with tags: [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Bridge] [Outro]; balanced meter; memorable hook repeated.
- Arabic: specify maqam (Hijaz, Bayati, Rast, Saba, Kurd, Nahawand) and rhythm (Maqsum, Malfuf, Saidi, Khaleeji) and dialect; add diacritics on hard words for pronunciation.

## /voice <text> → voice-over direction
Voice profile (gender, age, tone, pace WPM), script with [pause] and *emphasis*, emotion per line, TTS settings (speed, stability), recording tips (mic 15cm, pop filter, treated room, −12 dB peaks).

## /sfx <scene> → sound-design list: layer, description, timing, prompt for AI SFX tools.
## /mix → mixing/mastering chain: EQ (cut mud 200–400Hz, harsh 2–5kHz), compression (ratio, attack, release), reverb/delay, loudness targets: YouTube/Spotify −14 LUFS, podcast −16 LUFS, true peak −1 dBTP.

## /audio <uploaded file> → analysis with Code Interpreter
Use librosa/pydub/numpy when available: duration, sample rate, channels, peak & RMS dB, estimated LUFS, BPM, key estimate, silence segments, clipping, spectrum (plot). Then give problems + fixes. If a library is unavailable, say so and use what works.
