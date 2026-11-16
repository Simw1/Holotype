"""Assemble the Holotype early-grime dataset from the research batches.

Curated fields (display names, dates, lanes, draft codes, proposed type status) are set here;
sourced evidence (sound descriptions, context, relationships, URLs, uncertainty) comes from the batches.
Code tokens: '<allele index><basis>' where basis s = supported by a cited published description,
d = drafted by inference, awaiting confirmation by ear.
"""
import json, glob, os, re, sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, 'research', 'raw')
sys.path.insert(0, HERE)
from curation_round2 import NEW, LANES_EXTRA_FIRST, LANES_EXTRA_LAST, EDGES_NEW, OVERRIDE, PRODUCER_FIX, DROP_KEYS

recs = {}
for f in sorted(glob.glob(os.path.join(R, 'batch_*.json'))):
    for r in json.load(open(f)):
        recs[r['id_hint']] = r


# --- corrections from the independent fact-check (factcheck.md), 2026-11-16 ---
def fix(k, field, i, text, url=None):
    field = {'sound':'sound_descriptions'}.get(field, field)
    item = recs[k][field][i]; item['text'] = text
    if url: item['url'] = url
fix('dizzee-rascal-i-luv-u','context',2,"Self-produced, made earlier than the rest of Boy in da Corner, just after he dropped out of college, while on Deja Vu FM and associated with NASTY Crew.")
fix('wiley-eskimo','context',0,"Wiley told Martin Clark (Hyperdub, Nov 2003) that he made it at Christmas 1999 or 2000 and that it 'did 10,000' copies; he says he sold well over 50,000 records in total out of his car boot.")
fix('wiley-wot-do-u-call-it','sound',3,"PopMatters (Terry Sawyer, 2004 review) says it 'sounds like Mouse on Mars going insane inside a hip-hop song'.")
fix('wonder-what-dump-valve-2004','context',0,"Frieze calls it 'perhaps Dump Valve's definitive release' and its influence on South London dubstep 'immeasurable'.")
fix('wonder-what-dump-valve-2004','context',1,"Dump Valve was DJ Target's label, set up in 2001 by the Pay As U Go Cartel selector.")
fix('wonder-what-dump-valve-2004','context',2,"Recalling early grime's innovations, Slimzee lists 'What' alongside 'I Luv U' and 'Jam Hot'.")
fix('jon-e-cash-war-2003','context',2,"Shop copy for the reissue says he released the white labels of 'Drop Top Bimmer Kid' and named the style he fused from garage and hip-hop roots sublow.")
fix('more-fire-crew-oi-2002','context',1,"Wikipedia's More Fire Crew article calls it widely recognised as the first grime song to reach the UK Singles Chart.")
recs['more-fire-crew-oi-2002']['context'].append({'text':"Stereogum (2016) calls it 'the inaugural grime anthem'.",'url':'https://stereogum.com/1864651/10-essential-tracks-from-the-early-years-of-grime/lists'})
fix('roll-deep-the-avenue','context',1,"The first Roll Deep single without Dizzee Rascal; taken from In at the Deep End (Relentless/Virgin, 6 June 2005).","https://en.wikipedia.org/wiki/In_at_the_Deep_End")
fix('lethal-bizzle-pow-forward-2004','sound',1,"RA describes an 8-bar instrumental with a stark, bouncy synthline, claps and a militaristic fanfare. Its producer, D'Explicit, quoted by RA, says the bass enters with no intro and singles out the 808 kick as new to grime.")
fix('plasticman-venom-shockwave-2002','context',2,"Plasticman is from Thornton Heath, in the London Borough of Croydon, South London.")

# id_hint: (sortdate, date_display, kind, artist, title, label, cat, lane, codes, type)
T = {
 'more-fire-crew-oi-2002': ('2002-03-04','4 Mar 2002','Single','Platinum 45 feat. More Fire Crew','Oi!','Go! Beat','GOBCD48','garage',
   '1d 0s 0d 3d 0d 0d 0d 2d 0d 2s', ('Paralectotype','Grime',None,'Charted at no. 8 in March 2002 and widely called the first grime song in the UK chart, but sources also tag it UK garage. Kept in the type series as a transitional specimen; whether it outranks Pulse X on priority is a question for the panel.')),
 'musical-mob-pulse-x': ('2002-03-15','Mar 2002','12-inch','Musical Mob (Youngstar)','Pulse X','Inspired Sounds',None,'garage',
   '0d 0s 3s 0s 0d 0s 2s 0s 0s 0s', ('Proposed lectotype','Grime',None,'Earliest-dated record in this set that sources widely call the first grime beat (FACT no. 1; SPIN; Wikipedia) and described in an interview as the first 8-bar track released. No type was designated when the name grime came into use, so the first designation is a lectotype. Oi! (promo 2001) and Venom (made 2001, released early 2002) may predate it: see the priority question.')),
 'plasticman-venom-shockwave-2002': ('2002-04-01','Early 2002','12-inch','Plasticman','Venom / Shockwave','Slimzos',None,'dark',
   '0d 1d 1d 0d 0d 0d 0d 0s 0d 0d', ('Paralectotype','Grime','musical-mob-pulse-x','An early 2002 instrumental on Slimzee\'s label that its maker describes as an 8-bar grime track; extends the type series to South London.')),
 'danny-weed-creeper': ('2002-06-01','2002','12-inch','Danny Weed','Creeper','Roll Deep Recordings','RDR 001','melodic',
   '0d 1d 1d 0d 2s 1s 0d 0d 1s 0s', ('Paralectotype','Grime','musical-mob-pulse-x','A 2002 Roll Deep instrumental played heavily by Slimzee on Pay As U Go sets; adds the string-led strand to the type series.')),
 'wiley-eskimo': ('2002-07-01','Jul 2002','12-inch','Wiley','Eskimo','Wiley Kat Recordings (self-released)',None,'eski',
   '0d 4s 3s 0d 1s 0s 0d 0d 2d 0s', ('Proposed lectotype','Eskibeat',None,'Wiley chose the name eski beat for his sound and gave his tunes cold names (interview, November 2003). Eskimo is the first and best-known of that run, so it is proposed as the anchor; no record was designated at the time. Also a paralectotype of Grime: SPIN names it the rival contender to Pulse X as grime\'s founding track.')),
 'wiley-eskimo-2-devils-mix': ('2002-08-01','2002','12-inch','Wiley','Eskimo 2 (Devils Mix)','Wiley Kat',None,'eski',
   '0d 3s 3s 0d 1d 0d 0d 0d 0d 0s', ('Paralectotype','Eskibeat','wiley-eskimo','The devil mix: the same riddim with the drums removed. Shows how the eski B-side worked as a tool for MCs.')),
 'wiley-eskimo-3-ice-pole': ('2002-09-01','2002','12-inch','Wiley','Eskimo 3 / Ice Pole','Wiley Kat','WK007','eski',
   '0d 4d 3d 0d 0d 0s 0d 0s 0d 0s', ('Paralectotype','Eskibeat','wiley-eskimo','A sequel in the Eskimo series; release details rest on a single archived listing.')),
 'dizzee-rascal-i-luv-u': ('2002-10-01','2002 (test pressing); single 26 May 2003','Single','Dizzee Rascal','I Luv U','XL Recordings',None,'mc',
   '2s 4d 1d 2s 2s 1s 2s 2s 0d 1d', ('Paralectotype','Grime','musical-mob-pulse-x','A 2002 test pressing played on pirate radio before the 2003 single, which became Dizzee Rascal\'s first top 40 hit (no. 29), after Oi! had reached no. 8 in 2002.')),
 'wiley-ice-rink': ('2003-03-01','2003','12-inch','Wiley','Ice Rink','Wiley Kat',None,'eski',
   '0s 4s 3s 0d 4s 0s 0d 0d 0d 0s', ('Paralectotype','Eskibeat','wiley-eskimo','Minimal, melody-free eski instrumental with documented vocal EPs; FACT ranks it among Wiley\'s most powerful instrumentals.')),
 'plasticman-hard-graft-2003': ('2003-04-01','Apr 2003','12-inch','Plasticman','Hard Graft','Contagious Recordings','CONTAGIOUS-004','dark',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 0d', ('Voucher','Grime',None,'Evidence specimen. No published description of its sound was found, so every character is drafted.')),
 'mark-one-fight-terr001-2003': ('2003-05-01','2003','12-inch','Mark One','Fight / Fight (Plasticman Remix)','Terrorhythm Recordings','TERR001','dark',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 0d', ('Voucher','Grime',None,'Evidence specimen. No published description of its sound was found, so every character is drafted.')),
 'jon-e-cash-war-2003': ('2003-06-01','2003','12-inch','Jon E Cash','War','White label',None,'sublow',
   '0s 1d 1d 1d 0d 4s 0d 0d 0d 0d', ('Proposed lectotype','Sublow',None,'Jon E Cash is credited with inventing sublow, and War is among the best-known Black Ops productions. The case rests on record-shop and later sources (grade C); a stronger candidate may exist among earlier Black Ops white labels.')),
 'dizzee-rascal-boy-in-da-corner': ('2003-07-21','21 Jul 2003','Album','Dizzee Rascal','Boy in da Corner','XL Recordings',None,'mc',
   None, ('Context artefact','Grime',None,'Album: holds several specimens. Multi-track items are not coded as a single genotype.')),
 'dizzee-rascal-fix-up-look-sharp': ('2003-08-18','18 Aug 2003','Single','Dizzee Rascal','Fix Up, Look Sharp','XL Recordings',None,'mc',
   '2d 4s 1d 4d 4d None 4s 2d 1d 1s', ('Voucher','Grime',None,'Evidence specimen. Built on a rock record sample and tagged rap rock by some sources: a useful edge case for where grime\'s boundary sits.')),
 'nasty-crew-cock-back-2003': ('2003-09-01','Sep 2003','12-inch','Nasty Crew','Cock Back','Aftershock',None,'sublow',
   '0d 1d 2d 2d 4d 2d 1s 0d 2d 2s', ('Voucher','Grime',None,'Evidence specimen; produced by Terror Danjah, with documented later versions.')),
 'dizzee-rascal-jus-a-rascal': ('2003-11-24','24 Nov 2003','Single','Dizzee Rascal','Jus\' a Rascal','XL Recordings','XLS175CD','mc',
   '2d 1d 1d 2d 3d 5s 0s 2d 1d 3s', ('Voucher','Grime',None,'Evidence specimen. Played guitar and operatic elements; another boundary case.')),
 'wiley-wot-do-u-call-it': ('2004-04-05','5 Apr 2004','Single','Wiley','Wot Do U Call It?','XL Recordings','XLS179CD','eski',
   '0d 4d 2d 2s 0d 2s 0d 2s 2d 1s', ('Voucher','Eskibeat','wiley-eskimo','Vocal over the Igloo instrumental; Wiley\'s own record about what to call the sound.')),
 'wiley-treddin-on-thin-ice': ('2004-04-26','26 Apr 2004','Album','Wiley','Treddin\' on Thin Ice','XL Recordings',None,'eski',
   None, ('Context artefact','Eskibeat',None,'Album: holds reworked interludes of Eskimo and Ice Rink and the singles Wot Do U Call It? and Pies.')),
 'rephlex-grime-comp-cat156-2004': ('2004-05-01','2004','Compilation','Mark One, Plasticman, Slaughter Mob','Grime','Rephlex','CAT 156','dark',
   None, ('Context artefact','Grime',None,'An early use of the word grime as a release title, on an established electronic label: evidence for when and how the name was fixed.')),
 'wiley-pies': ('2004-06-01','2004','12-inch','Wiley','Pies','XL Recordings',None,'eski',
   '0d 4d 2d 0d 4s 2s 0d 2d 2s 1d', ('Voucher','Eskibeat','wiley-eskimo','Evidence specimen; its B-side is a vocal version of Terror Danjah\'s Creepy Crawler.')),
 'terror-danjah-industry-standard-ep-2004': ('2004-07-01','2004','12-inch EP','Terror Danjah','Industry Standard EP','Aftershock',None,'sublow',
   '0d 1d 2d 0d 3d 4s 0d 3d 2d 0d', ('Voucher','Grime',None,'Coded for Creepy Crawler, the track with documented vocal versions.')),
 'wonder-what-dump-valve-2004': ('2004-08-01','2004','12-inch','Wonder','What','Dump Valve',None,'sino',
   '0d 1d 1d 1d 1s 0s 0d 3d 1d 0s', ('Candidate','Sino-grime',None,'Oriental chimes over dense bass make it the strongest candidate here, but no source calls it sino-grime by name. Left as a candidate until the panel decides.')),
 'plasticman-cha-ep-terr002': ('2004-08-15','2004','12-inch EP','Plasticman','Cha EP','Terrorhythm Recordings','TERR002','dark',
   '0d 1d 1d 1d 0d 0d 0d 0d 0d 0d', ('Voucher','Grime',None,'Coded for the title track; every character is drafted, as no track-level description was found.')),
 'xtc-functions-on-the-low': ('2004-09-01','2004','12-inch','XTC','Functions on the Low','White label',None,'melodic',
   '0d 1d 1d 0d 3d 0s 2s 3d 1d 0s', ('Voucher','Grime',None,'Evidence specimen; its instrumental was reused for Stormzy\'s Shut Up (2015).')),
 'mark-one-one-way-ziq112': ('2004-09-27','27 Sep 2004','Album','Mark One','One Way','Planet Mu','ZIQ112','dark',
   None, ('Context artefact','Grime',None,'Album on an electronic label; documents grime instrumentals reaching a wider electronic audience.')),
 'jammer-destruction-vip': ('2004-10-01','2004','12-inch','Jammer feat. Wiley, D Double E, Kano and Durrty Goodz','Destruction VIP','JahmekTheWorld',None,'mc',
   '0d 1d 1d 2d 0d 0d 0d 0d 0d 2s', ('Voucher','Grime',None,'Evidence specimen; a posse track later compiled on Run the Road.')),
 'lethal-bizzle-pow-forward-2004': ('2004-10-25','25 Oct 2004 (digital)','Single','Lethal Bizzle','Pow! (Forward)','Relentless Records','RELDX15','garage',
   '0d 1d 1d 0d 0d 0s 0d 0s 0d 2s', ('Voucher','Grime',None,'An eight-bar rally over Dexplicit\'s Forward Riddim; its producer singles out the 808 kick as new to grime.')),
 'kano-ps-and-qs-2004': ('2004-11-01','Nov 2004','Single','Kano','P\'s and Q\'s','679 Recordings',None,'mc',
   '0d 1d 2d 0s 0d 0s 0d 0d 0d 1s', ('Voucher','Grime',None,'Evidence specimen; produced by DaVinChe.')),
 'ruff-sqwad-anna': ('2004-12-01','2004','Single','Ruff Sqwad','Anna / Down',None,None,'melodic',
   '0d 1d 1d 0d 0s 0s 0d 0d 1d 2d', ('Voucher','Grime',None,'Release details provisional: only Wikipedia gives a date, and the label is unconfirmed.')),
 'lord-of-the-mics-1-2004': ('2004-12-15','2004','DVD','Jammer (creator), with Ratty and Capo','Lord of the Mics (Vol. 1)','Self-released',None,'mc',
   None, ('Context artefact','Grime',None,'A clash DVD, not a record: evidence of how MC battles circulated and were seen.')),
 'jammer-murkle-man': ('2005-01-01','c. 2004 to 2005','Single','Jammer','Murkle Man',None,None,'mc',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 1d', ('Voucher','Grime',None,'Release details provisional, and the producer credit is disputed between sources.')),
 'run-the-road-2005': ('2005-01-24','24 Jan 2005','Compilation','Various artists','Run the Road','679 Recordings',None,'mc',
   None, ('Context artefact','Grime',None,'Compilation on the independent label 679, called the scene-defining survey and the first widely available in the US (Reynolds, Spin, 2005). Holds versions of several specimens.')),
 'kano-typical-me-2005': ('2005-02-28','28 Feb 2005','Single','Kano feat. Ghetto','Typical Me','679 Recordings','679L096CD1','mc',
   '2d 1d 1d 2d 3d 5d 0d 2d 1d 2s', ('Voucher','Grime',None,'Evidence specimen; no description of the beat was found, so most characters are drafted.')),
 'ruff-sqwad-guns-and-roses-vol-1': ('2005-03-04','4 Mar 2005','Mixtape','Ruff Sqwad','Guns and Roses Volume. 1','Ruff Sqwad Recordings',None,'melodic',
   None, ('Context artefact','Grime',None,'Mixtape CD: documents the crew\'s sample-led romantic phase.')),
 'lady-sovereign-random-2005': ('2005-03-14','14 Mar 2005','Single','Lady Sovereign','Random','Casual Records',None,'mc',
   '2d 4s 2d 0d 0d 2s 0d 2d 2d 1s', ('Voucher','Grime',None,'Evidence specimen; sources tag it electronic, hip hop and grime.')),
 'kano-home-sweet-home-2005': ('2005-06-27','27 Jun 2005','Album','Kano','Home Sweet Home','679 Recordings',None,'mc',
   None, ('Context artefact','Grime',None,'Album; Kano said before release that he did not see himself as a grime artist, which bears on how far the label should reach.')),
 'roll-deep-the-avenue': ('2005-07-18','18 Jul 2005','Single','Roll Deep','The Avenue','Relentless Records',None,'melodic',
   '1d 1d 0d 3d 3d 3d 4s 2d 1d 3d', ('Voucher','Grime',None,'Evidence specimen; samples a 1983 pop record and is tagged grime and neo soul.')),
 'roll-deep-when-im-ere': ('2005-07-19','2005','Single','Roll Deep','When I\'m \'Ere','Relentless Records',None,'melodic',
   '0d 1d 1d 0d 0d 5s 0d 0s 2s 2s', ('Voucher','Grime',None,'Evidence specimen; a relay of crew MCs over an accordion lead.')),
 'kamikaze-ghetto-kyote-2005': ('2005-09-01','2005','12-inch','Kamikaze (Treble Clef)','Ghetto Kyote','White label',None,'sino',
   '0d 1d 3d 1d 0d 0d 0d 3d 1d 0s', ('Voucher','Grime',None,'Evidence specimen; a later Kano vocal is documented.')),
 'ruff-sqwad-died-in-ur-arms': ('2006-10-13','13 Oct 2006','Mixtape track','Ruff Sqwad','Died in Ur Arms','Ruff Sqwad Recordings',None,'melodic',
   '0d 1d 1d 0d 3s 0d 4s 3d 1d 0d', ('Voucher','Grime',None,'Evidence specimen; samples a 1980s power ballad.')),
 'ruff-sqwad-pied-piper': ('2002-11-01','c. 2002 (made)','12-inch','Ruff Sqwad','Pied Piper','Ruff Sqwad Recordings (unconfirmed)',None,'melodic',
   '0d 1d 3d 0d 0d 0s 0d 0d 0d 0s', ('Voucher','Grime',None,'Release details provisional: made around 2002 according to its producer, but the release date and label are unconfirmed.')),
}

LANES = [
 ('garage','Garage and 8-bar'),('eski','Eskibeat'),('melodic','Bow melodic'),
 ('sublow','Sublow and war'),('sino','Sino and haunted'),('dark','South London'),('mc','MC releases')]

EDGES = [
 ('wiley-eskimo','wiley-eskimo-2-devils-mix','version','Devil mix: the same riddim without drums'),
 ('wiley-eskimo','wiley-eskimo-3-ice-pole','inherit','Sequel in the Eskimo series'),
 ('wiley-eskimo','wiley-treddin-on-thin-ice','contains','Reworked as an interlude on the album'),
 ('wiley-ice-rink','wiley-treddin-on-thin-ice','contains','Reworked as an interlude on the album'),
 ('wiley-wot-do-u-call-it','wiley-treddin-on-thin-ice','contains','Single from the album'),
 ('wiley-pies','wiley-treddin-on-thin-ice','contains','Single from the album'),
 ('terror-danjah-industry-standard-ep-2004','wiley-pies','version','Creepy Crawler voiced by Wiley as Take Chances, the B-side of Pies'),
 ('musical-mob-pulse-x','dizzee-rascal-i-luv-u','transfer','Combined on a 2003 white-label mash-up'),
 ('musical-mob-pulse-x','wiley-eskimo','transfer','Combined in the later mash-up Pulse Eskimo (Gun Shot Riddim)'),
 ('dizzee-rascal-i-luv-u','dizzee-rascal-boy-in-da-corner','contains','Lead single of the album'),
 ('dizzee-rascal-fix-up-look-sharp','dizzee-rascal-boy-in-da-corner','contains','Single from the album'),
 ('dizzee-rascal-jus-a-rascal','dizzee-rascal-boy-in-da-corner','contains','Single from the album'),
 ('kano-ps-and-qs-2004','run-the-road-2005','contains','Compiled as track 4'),
 ('kano-ps-and-qs-2004','kano-typical-me-2005','contains','B-side of the CD single'),
 ('kano-ps-and-qs-2004','kano-home-sweet-home-2005','contains','Album track'),
 ('kano-typical-me-2005','kano-home-sweet-home-2005','contains','Album track'),
 ('jammer-destruction-vip','run-the-road-2005','contains','Compiled on Run the Road'),
 ('nasty-crew-cock-back-2003','run-the-road-2005','version','Cock Back V1.2 compiled on Run the Road'),
 ('more-fire-crew-oi-2002','lethal-bizzle-pow-forward-2004','inherit','Solo single by a More Fire Crew member, with Ozzie B and Neeko featured'),
 ('plasticman-hard-graft-2003','mark-one-fight-terr001-2003','transfer','Plasticman and Mark One remix each other\'s records'),
 ('roll-deep-when-im-ere','roll-deep-the-avenue','contains','B-side of the CD single'),
]

A_DOMAINS = ('officialcharts.com','chantellefiddy','fiddy','gridface','k-punk','simonreynolds','blissblog')
CONTEMP = r'\b(spin|popmatters|vice|i-d|k-punk|fiddy|gridface|martin clark|hyperdub|grimewatch|billboard|pitchfork|village voice|reynolds)\b[^.]{0,45}\b200[2-6]\b'
def grade(text, url):
    """A = published at the time (2002-06) or an official chart record; B = a maker or participant recalling later;
    C = later journalism, reference works, shop listings."""
    t = (text or '').lower(); u = (url or '').lower()
    if any(d in u for d in A_DOMAINS): return 'A'
    if re.search(r'/200[2-6]/', u): return 'A'
    if re.search(CONTEMP, t) or re.search(r'\b200[2-6] (review|lecture|post)\b', t) or re.search(r'\bin 200[2-6],? (wiley|plastician|jammer|kano|dizzee)', t):
        return 'A'
    if re.match(r'(wikipedia|complex|mixmag|fact)\b', t):
        return 'C'
    if re.search(r'\b(told|recalls?|recalled|says he|says it was|interview|describes his|plastician (says|describes|called|sent)|producer says|dates it|jammer \(|dizzee:|dizzee says)', t):
        return 'B'
    return 'C'

def domain(u):
    try:
        n = urlparse(u).netloc.replace('www.','')
        if 'ipfs' in n or 'wikipedia' in u.lower(): return 'wikipedia (mirror)' if 'wikipedia.org' not in n else n
        return n
    except Exception: return u

def codes(s):
    if s is None: return None
    out = []
    for tok in s.split():
        if tok == 'None': out.append(None); continue
        out.append({'a': int(tok[:-1]), 'b': tok[-1]})
    return out

# ---------------------------------------------------------------- round 2 build
ROUND1 = sorted(T, key=lambda k: T[k][0])             # accession numbers HT-G001..041 are permanent
for k, v in OVERRIDE.items():
    t = list(T[k]); st = list(t[9])
    for f, val in v.items():
        if f == 'date': t[1] = val
        elif f == 'kind': t[2] = val
        elif f == 'artist': t[3] = val
        elif f == 'label': t[5] = val
        elif f == 'codes': t[8] = val
        elif f == 'basis': st[3] = val
    t[9] = tuple(st); T[k] = tuple(t)
for k in PRODUCER_FIX: recs[k]['producers'] = PRODUCER_FIX[k]
ROUND2 = sorted(NEW, key=lambda k: NEW[k][0])
T.update(NEW)
LANES = LANES_EXTRA_FIRST + LANES + LANES_EXTRA_LAST
EDGES = EDGES + EDGES_NEW
idmap = {k: f'HT-G{n:03d}' for n, k in enumerate(ROUND1 + ROUND2, 1)}
ids = sorted(T, key=lambda k: T[k][0])
missing = [k for k in T if k not in recs]
if missing: sys.exit('missing research for: %s' % missing)

# fact-check results: (key, field, index) -> correction
CHK = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'research', 'checks', 'h*.json'))):
    for c in json.load(open(f)):
        if c.get('field') in ('sound', 'context') and c.get('index') is not None:
            CHK[(c['key'], c['field'], c['index'])] = c

def evidence(k, field, items):
    res = []
    for i, x in enumerate(items):
        c = CHK.get((k, field, i))
        e = {'text': x['text'], 'url': x['url'], 'g': grade(x['text'], x['url']), 'checked': False}
        if c:
            if c['verdict'] == 'unsupported' and not c.get('new_text'):
                continue
            if c.get('new_text'): e['text'] = c['new_text']
            if c.get('new_url'): e['url'] = c['new_url']
            if c.get('grade') in ('A', 'B', 'C'): e['g'] = c['grade']
            if c.get('pub_date'): e['pub'] = str(c['pub_date'])
            e['checked'] = c['verdict'] in ('supported', 'partly')
        res.append(e)
    return res

# platform audit -------------------------------------------------------------
LAB = []
for f in sorted(glob.glob(os.path.join(ROOT, 'research', 'audit-labels-round*.json'))):
    LAB += json.load(open(f))
GRIME_OK = ('grime', 'eskibeat', 'eski', 'sublow', 'sinogrime', 'sino-grime')
ADJ = ('garage', 'uk garage', '2-step', 'dubstep', 'uk bass', 'bass music', 'uk hip hop', 'uk hip-hop', 'uk rap', 'bassline')
BROAD = ('electronic', 'dance', 'hip-hop/rap', 'hip-hop', 'hip hop', 'rap', 'r&b/soul', 'r&b', 'urban', 'electronica', 'beats', 'instrumental', 'experimental', 'alternative')
WRONG = ('rock', 'pop', 'house', 'd&b', 'drum & bass', 'drum and bass', 'reggae', 'jazz', 'soul', 'world', 'dancehall', 'grindnoise', 'techno', 'trance')
SCORE = {'correct': 1.0, 'adjacent': 0.5, 'broad': 0.25, 'wrong': 0.0}
def classify(label, target):
    l = label.lower().strip()
    if target == 'UK garage':
        if 'garage' in l or '2-step' in l: return 'correct'
        if any(g in l for g in GRIME_OK): return 'adjacent'
    elif target == 'transition':
        if 'garage' in l or any(g in l for g in GRIME_OK): return 'correct'
    else:
        if any(g in l for g in GRIME_OK): return 'correct'
        if any(l == a or a in l for a in ADJ): return 'adjacent'
    if l in BROAD or any(l == b for b in BROAD): return 'broad'
    if any(l == w or w in l.split('/') for w in WRONG): return 'wrong'
    return None   # not a genre term (place names, artist names, formats)
def verdict(labels, target):
    vs = [classify(x, target) for x in labels]
    vs = [v for v in vs if v]
    if not vs: return 'no genre'
    return max(vs, key=lambda v: SCORE[v])     # a tag list is credited with its best genre term

out = []
for k in ids:
    sd, ddisp, kind, artist, title, label, cat, lane, cs, ty = T[k]
    r = recs[k]
    status, of, holo, basis = ty
    sound = evidence(k, 'sound', r.get('sound_descriptions') or [])
    ctx = evidence(k, 'context', r.get('context') or [])
    urls = []
    for u in (r.get('other_source_urls') or []) + [x['url'] for x in sound] + [x['url'] for x in ctx]:
        if u and u not in urls: urls.append(u)
    target = 'UK garage' if status == 'Outgroup' or of == 'UK garage' else ('transition' if status == 'Transitional' else 'Grime')
    aud = []
    for x in LAB:
        if x['key'] != k or x['status'] == 'not_accessible': continue
        a = {'platform': x['platform'], 'status': x['status'], 'labels': x.get('labels') or [], 'match': x.get('match_quality'),
             'release': x.get('matched_release'), 'level': x.get('level'), 'url': x.get('url'), 'retrieved': x.get('retrieved')}
        if x['status'] == 'found':
            a['verdict'] = verdict(a['labels'], target) if a['match'] != 'uncertain' else 'uncertain match'
        aud.append(a)
    out.append({
        'id': idmap[k], 'key': k, 'sort': sd, 'year': int(sd[:4]), 'date': ddisp, 'kind': kind,
        'artist': artist, 'title': title, 'label': label, 'cat': cat, 'format': r.get('format'),
        'producers': r.get('producers') or [], 'lane': lane, 'geno': codes(cs),
        'type': {'status': status, 'of': of, 'holotype': idmap.get(holo) if holo else None, 'basis': basis},
        'sound': sound, 'context': ctx,
        'calls': [{'label': c.get('label'), 'source': c.get('source'), 'year': c.get('year'), 'url': c.get('url')} for c in (r.get('genre_calls') or [])],
        'rels': [{'type': x.get('type'), 'other': x.get('other'), 'url': x.get('url')} for x in (r.get('relationships') or [])],
        'uncertainty': r.get('uncertainty'), 'tracklist': r.get('tracklist_note'),
        'sources': [{'url': u, 'domain': domain(u)} for u in urls],
        'audit': aud, 'round': 1 if k in ROUND1 else 2,
    })

# audit summary by platform (Bandcamp tags are uploader-chosen, reported separately)
summ = {}
for s in out:
    for a in s['audit']:
        p = summ.setdefault(a['platform'], {'listed': 0, 'absent': 0, 'scored': 0, 'score': 0.0, 'verdicts': {}, 'labels': {}})
        if a['status'] == 'not_available': p['absent'] += 1; continue
        p['listed'] += 1
        v = a.get('verdict'); p['verdicts'][v] = p['verdicts'].get(v, 0) + 1
        for l in a['labels']: p['labels'][l] = p['labels'].get(l, 0) + 1
        if v in SCORE: p['scored'] += 1; p['score'] += SCORE[v]
for p in summ.values():
    p['fidelity'] = round(100 * p['score'] / p['scored']) if p['scored'] else None
    p['grime_named'] = sum(n for l, n in p['labels'].items() if any(g in l.lower() for g in GRIME_OK))

edges = [{'f': idmap[a], 't': idmap[b], 'k': kk, 'note': n} for a, b, kk, n in EDGES]
data = {'version': '0.2', 'built': '2026-11-17', 'loci': json.load(open(os.path.join(ROOT, 'data', 'loci.json'))),
        'lanes': [{'k': a, 'name': b} for a, b in LANES], 'specimens': out, 'edges': edges,
        'audit': {'platforms': summ, 'scores': SCORE,
                  'rules': 'A label naming grime or a grime sub-style is correct (garage, for UK garage outgroups); a neighbouring genre is adjacent; an umbrella term is broad; an unrelated genre is wrong. A tag list is credited with its best genre term. Uncertain matches are not scored.'}}

os.makedirs(os.path.join(ROOT, 'data', 'specimens'), exist_ok=True)
for s in out:
    json.dump(s, open(os.path.join(ROOT, 'data', 'specimens', s['id'] + '.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(data, open(os.path.join(ROOT, 'data', 'register.json'), 'w'), ensure_ascii=False, indent=1)

# checks
for s in out:
    if s['geno'] is not None:
        assert len(s['geno']) == 10, s['key']
        for i, c in enumerate(s['geno']):
            if c: assert c['a'] < len(data['loci'][i]['alleles']), (s['key'], i)
from collections import Counter
print(len(out), 'specimens;', sum(1 for s in out if s['geno']), 'coded;', len(edges), 'edges')
print(Counter(s['type']['status'] for s in out))
print(Counter(x['g'] for s in out for x in s['sound'] + s['context']), 'checked', sum(x['checked'] for s in out for x in s['sound'] + s['context']))
for k, p in summ.items(): print(k, {kk: p[kk] for kk in ('listed', 'absent', 'fidelity', 'grime_named', 'verdicts')})
