# holotype-ingest

**Status: prototype, version 0.1.** Tested end to end on synthetic audio with known answers; not yet run on real recordings.

This turns audio into proposals for the register. The audio can be vinyl rips, tape rips or whole pirate radio sets. Nothing enters the register automatically: every proposal waits in a review queue for a person to accept or reject it.

## What it does

| Step | How |
|---|---|
| Seal | SHA-256 of the file, written to a hash-chained, append-only log (`log.jsonl`; check it with `verify`) |
| Separate | Splits the vocal from the instrumental: Demucs if installed, otherwise REPET-SIM. REPET-SIM treats what repeats as backing and what doesn't as voice, which suits loop-built riddims |
| Fingerprint | Landmark (Shazam-style) hashes in three profiles. **full** identifies a recording. **riddim** (30–300 Hz, from the instrumental) identifies the instrumental under an MC. **vocal** (from the vocal stem) tells a copy from a different vocal over the same riddim |
| Match | Votes on consistent time offsets against known specimens and every earlier upload, searching playback speed (0.90–1.10) for pitched or worn vinyl. A match must stand out from the index background and cover enough of the recording |
| Decide the relation | *Same recording*, *same riddim (different version or vocal)*, or *possible match*, with the reason and the playback speed |
| Sets | Recordings over 8 minutes, or anything passed with `--set`, are cut into 20-second windows, matched, and merged into "what plays when" segments. A candidate an earlier upload linked to a specimen points through to that specimen |
| Measure | Tempo (tracked from the drum bands, so an MC can't throw it), loudness, crest, sub-bass share, a 16-step drum profile, bass harmonics (from the instrumental) and section length |
| Draft codes | Drafts TMP, KCK, HAT, BAS, STR and VOC from the measurements, each with a confidence and a reason. Basis: machine, to be confirmed by ear |
| Transcribe | Optional Whisper transcript (`--transcribe`), treated as a draft: it handles MLE and patois badly |
| Queue | One JSON file per upload, plus `queue/review.html` |

The index holds fingerprints, never audio, and fingerprints can't be turned back into sound. Contributors can keep their recordings while the register still recognises them.

## Use

```
pip install -r requirements.txt          # numpy, scipy, librosa, soundfile; ffmpeg on the PATH
cd ingest
python3 -m holotype_ingest --root ~/holotype-data index "~/rips/HT-G002 Pulse X.wav"   # id from the filename, or --id
python3 -m holotype_ingest --root ~/holotype-data scan ~/rips/new/                     # tracks and sets
python3 -m holotype_ingest --root ~/holotype-data scan --set "~/tapes/rinse 2003-04-12.mp3"
python3 -m holotype_ingest --root ~/holotype-data review                               # writes queue/review.html
python3 -m holotype_ingest --root ~/holotype-data decide 6caf73eb3576 0 accept --note "confirmed by ear" --reviewer SW
python3 -m holotype_ingest --root ~/holotype-data verify
```

Optional extras: `pip install demucs` (better separation; downloads a model the first time) and `pip install openai-whisper` (transcripts).

## Test

```
tests/run_test.sh /tmp/ht-test
```

This generates synthetic material with known answers and checks six outcomes:

- A vocal version matches its riddim and is not mistaken for a copy.
- A worn vinyl copy played 6% fast is identified, with its speed measured.
- An unknown riddim produces no false match.
- A later vocal over that unknown riddim is matched to it.
- Tempo is read correctly under an MC.
- A mock pirate set comes back in the right order.

All six pass.

## Known limits

- Thresholds are tuned on synthetic audio and need re-tuning on real recordings, especially old off-air cassettes.
- Set segment boundaries are accurate to about ±10 seconds, because the windows are 20 seconds long with 10-second steps.
- Drafted drum, hat and bass codes are heuristics. Their confidence scores are low on purpose.
- REPET-SIM is weaker than Demucs on records that don't loop. Use Demucs for serious runs.
- It matches recordings and riddims. It does not yet match the same musical idea played differently, such as a re-lick or an interpolation. That is the next layer.
