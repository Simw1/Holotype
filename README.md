# Holotype

**A reference register for Black British music. Proof of concept: early grime and its garage roots, 2000–2006.**

Holotype holds real releases as register entries. Each entry carries:

- **Sealed evidence**: release facts, and published evidence of how the record sounded and was heard. Every item is linked to its source and graded by when that source was published.
- **A genotype**: a ten-character musical profile (tempo, drums, bass, harmony, lead sound, sampling, structure, effects, vocal). Each character is marked *sourced* (supported by a published description) or *drafted* (awaiting confirmation by ear).
- **A type status**: a proposed place in a type series that anchors genre names to dated records, borrowed from biological nomenclature (lectotype, paralectotype, voucher, outgroup).
- **A platform audit**: what public music platforms call the same record.
- **A provenance log**: an append-only history of the entry. Git history is the durable version of that log.

## What's in v0.2

| | |
|---|---|
| Specimens | 68 releases, 2000–2006, accession numbers HT-G001 to HT-G068 (permanent) |
| Coded | 52 single-record specimens; 16 albums, compilations, mixtapes and one DVD held as context artefacts |
| Evidence | Graded A (published at the time), B (a maker recalling later), C (later journalism, reference works, shop listings) |
| Type proposals | Grime (proposed lectotype: Pulse X), Eskibeat (Eskimo), Sublow (War), Sino-grime (candidate), with UK garage outgroups and five transitional records |
| Audit | Apple Music, Qobuz and Bandcamp, collected November 2026 from pages and APIs open without logging in |

## What is provisional

- **Codes**: most musical codes are drafts. `docs/coding-sheet.csv` is the listening sheet for confirming them by ear.
- **Type statuses**: these are proposals for review by people from the scene, not decisions. The first open question is where grime begins: Pulse X (2002) or one of the transitional records from 2000–01.
- **Catalogue numbers**: often missing, because Discogs and MusicBrainz could not be reached during research.
- **Sound measurements**: none yet, as no audio is held.

## Layout

```
data/
  register.json        everything, as one file (the site is built from this)
  specimens/HT-G###.json   one file per specimen
  loci.json            the coding scheme (v0.1, grime-specific)
research/
  raw/                 research batches as gathered, with every source URL
  checks/              independent fact-check results (h1–h5) and the first-round report
  audit-labels-*.json  platform labels exactly as collected
scripts/
  build_data.py        assembles the register: applies curation, fact-check corrections, grades and audit scoring
  curation_round2.py   round-two curation and corrections
  build_page.py        builds site/index.html and docs/coding-sheet.csv
  template.html        the register page
site/index.html        the register, as a single self-contained page
docs/coding-sheet.csv  listening sheet
```

## Rebuild

```
python3 scripts/build_data.py && python3 scripts/build_page.py
```

No dependencies beyond Python 3. To publish, point Vercel (or GitHub Pages) at `site/`.

## Method notes

- Grades go by the page that can actually be cited. A 2003 interview known only through a 2014 reprint is graded by the reprint, and the original is noted.
- Platform labels are scored against the register's placement as correct, adjacent, too broad or wrong. Bandcamp tags are chosen by uploaders, so they are reported separately from genres set by platforms.
- The biology terms give the evidence a structure. They describe recordings, never people.

## Licences

Code is under the MIT licence. Data is under CC BY 4.0. Quotations remain the copyright of their publishers. See `LICENSE.md`.

Built by Simon Westgate, with AI-assisted desk research, November 2026.
