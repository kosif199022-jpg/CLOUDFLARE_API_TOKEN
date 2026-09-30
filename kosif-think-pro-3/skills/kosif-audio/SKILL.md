---
name: kosif-audio
description: Use for any audio task — analyzing an uploaded audio file (loudness, peaks, BPM, clipping, spectrum), mixing/mastering advice, songs and lyrics (Suno/Udio), Arabic maqam and rhythm, voice-over scripts and TTS direction, podcast production, sound effects and sound design for video. Triggers on /audio /master /mix /song /voice /sfx /podcast, "صوت", "أغنية", "موسيقى", "تعليق صوتي", "ماسترينغ".
---
# KOSIF Audio Lab

## /audio <file> — measured analysis
Run `scripts/audio_analyze.py FILE --summary [--target streaming|podcast|broadcast|club] [--plot out.png]` (numpy; WAV natively, MP3/M4A via soundfile or ffmpeg if installed — otherwise ask for WAV).
It measures: duration, sample rate, bit depth, channels · sample peak and 4× oversampled true peak · RMS, crest factor · integrated loudness (BS.1770-4 K-weighting + gating) · gain to target · DC offset · clipped samples · silence segments · stereo correlation and L/R balance · spectral centroid and band shares (sub/bass/low-mid/mid/presence/air) · tempo estimate (onset autocorrelation, with confidence).
Report: numbers table → problems (with the measured evidence) → exact fix chain → export settings. Show the plot when produced.
The meter follows BS.1770 closely but is not certified; tempo is an estimate — say so.

## Loudness targets
Spotify/YouTube/Apple ≈ −14 LUFS, TP ≤ −1 dBTP · Podcast −16 LUFS (mono −19) · Broadcast EBU R128 −23 LUFS, TP −1 · Club/DJ −9 to −6 LUFS, TP −0.3.

## /master and /mix — processing chain
1. Clean: high-pass 20–30 Hz (80–100 Hz for voice), remove DC, de-click/de-noise.
2. EQ: cut mud 200–400 Hz, boxiness 400–800 Hz, harshness 2.5–5 kHz; add air shelf 10–12 kHz gently.
3. Dynamics: compressor (voice 3:1, attack 10 ms, release 80 ms, 3–6 dB GR; mix bus 2:1, 1–2 dB GR); de-esser 5–8 kHz.
4. Space: short room/plate reverb, pre-delay 20–40 ms; delay synced to BPM (ms = 60000 / BPM).
5. Master: glue compression → EQ → limiter ceiling = target TP → loudness to target (use gain_to_target_db).
6. Export: WAV 24-bit/48 kHz master; MP3 320 kbps or AAC 256 kbps for delivery.

## /song <idea> — Suno/Udio-ready package
- Title · **Style prompt** (English ≤ 200 chars: genre, sub-genre, mood, BPM, key, instruments, vocal type/gender, production era) · **Exclude styles**.
- Lyrics with tags `[Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Bridge] [Final Chorus] [Outro]`; syllable-balanced lines; a hook repeated 2–4×; rhyme scheme stated.
- Arabic: dialect (Khaleeji, Egyptian, Levantine, Iraqi, Sudanese, Maghrebi, Fusha), maqam and rhythm from `references/arabic-music.md`; add tashkeel on words likely to be mispronounced; avoid rare words the model may garble.
- Alternative version (different genre) + a 15-second hook for reels.

## /voice <text> — voice-over direction
Voice profile (gender, age range, tone, accent/dialect, pace in WPM: ads 150–170, narration 130–150, meditation 100–120) · script marked with `[pause 0.5s]`, *emphasis*, (emotion) per line · TTS settings (stability/similarity/style/speed) · recording: cardioid mic 10–15 cm, pop filter, treated corner, peaks around −12 dBFS, 48 kHz/24-bit.

## /sfx <scene> — sound design sheet
Table: timecode · layer (ambience/foley/hard FX/music/UI) · description · level (dBFS) · pan · prompt for AI SFX tools (ElevenLabs SFX, Stable Audio).

## /podcast — episode production plan: structure, intro/outro music cues, levels, noise floor target (< −60 dBFS), chapter markers, show notes.

## Limits
ChatGPT cannot play or synthesize audio natively unless an audio tool is exposed; when it is not, deliver scripts/prompts/settings and say generation must happen in Suno/TTS tools. Never claim to have listened beyond the measured numbers.
