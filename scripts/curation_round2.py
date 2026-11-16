"""Round 2 curation: 27 new specimens (garage transition, 2005-06 wave, producers), fact-check overrides,
extra lanes and documented links. Imported by build_data.py.

Tuple layout matches build_data.T:
(sortdate, date_display, kind, artist, title, label, cat, lane, codes, (status, of, anchor_key, basis))
"""

OUT = "Outgroup"      # UK garage reference specimens used to root the analysis
TRN = "Transitional"  # sources split between UK garage and grime

NEW = {
 # --- garage transition, 2000-02 ---
 'oxide-neutrino-bound-4-da-reload-2000': ('2000-05-06','2000 (chart entry 6 May 2000)','Single','Oxide & Neutrino','Bound 4 Da Reload (Casualty)','East West',None,'transition',
   '1d 0d 0d 1s 4d 3d 1s 3d 2s 1s', (OUT,'UK garage',None,'A no. 1 garage hit built on a TV-theme and film sample. Sources file it as 2-step garage; one later reader comment calls it proto-grime. Held as an outgroup: a garage reference point against which grime\'s characters can be compared.')),
 'pay-as-u-go-know-we-2000': ('2000-06-01','2000 (Reynolds gives 2001)','12-inch','Pay As U Go Cartel','Know We','Solid City (per Reynolds; FACT says self-released)',None,'transition',
   '1d 1d 3d 1d 2s 1s 0s 0d 0d 2s', (TRN,'Grime',None,'Produced by Wiley. Reynolds lists it in his 2005 Grime Primer as garage rap; FACT (2013) calls it vanguard grime. Its string hook and MC-first space anticipate Wiley\'s later records.')),
 'so-solid-crew-oh-no-dilemma-2000': ('2000-12-16','2000 (chart entry 16 Dec 2000)','Single','So Solid Crew','Oh No (Sentimental Things) / Dilemma','Relentless','RELENT8CDS','transition',
   '1d 0s 3s 0d 4d 0d 0d 0d 0d 2s', (TRN,'Grime',None,'Coded for Dilemma. Kode9 called it ultra-minimal in 2001; FACT (2013) calls it a proto-grime flip; the Quietus (2020) reports Wiley saying Oh No started grime. A strong candidate for the earliest record in the grime type series.')),
 'genius-cru-boom-selection-2001': ('2001-02-03','2001 (chart entry 3 Feb 2001)','Single','Genius Cru','Boom Selection','Incentive (Kronik)','CENT17CDS','transition',
   '1d 0d 0d 3d 0d 0d 4s 2d 0d 2d', (OUT,'UK garage',None,'A garage-rap chart hit; sources call it UK garage and place it before the grimy era. Held as an outgroup.')),
 'so-solid-crew-21-seconds-2001': ('2001-08-06','6 Aug 2001','Single','So Solid Crew','21 Seconds','Relentless','RELENT16CD','transition',
   '0s 0s 0d 3d 0d 3s 0d 0s 0d 2s', (OUT,'UK garage',None,'A no. 1 garage single at about 140 BPM with each MC taking a short slot. Sources call it garage that helped usher in what became grime. Held as an outgroup; its tempo and 8-bar relay already match grime\'s.')),
 'jaimeson-urban-hero-2001': ('2001-08-25','2001 (chart entry 25 Aug 2001)','Single','Jaimeson','Urban Hero (with Slow Jam)','Lifestyle (per FACT)',None,'transition',
   '1d 0d 0d 3d 0d 0d 0d 2d 0d 3d', (OUT,'UK garage',None,'FACT (2013) places it in the period when garage was spawning grime. Held as an outgroup; little is known of its sound, so every code is drafted.')),
 'so-solid-crew-they-dont-know-album-2001': ('2001-11-19','19 Nov 2001','Album','So Solid Crew','They Don\'t Know','Independiente / Relentless',None,'transition',
   None, ('Context artefact','UK garage',None,'Album: the Quietus (2020) hears grime avant la lettre in tracks such as Deeper. Multi-track items are not coded as one profile.')),
 'oxide-neutrino-rap-dis-2001': ('2001-12-08','2001 (chart entry 8 Dec 2001)','Single','Oxide & Neutrino feat. So Solid members','Rap Dis','East West','OXIDE08CD1','transition',
   '1d 4d 2d 0d 2s 1s 0d 0d 0d 2s', (TRN,'Grime',None,'Trench (2021) describes garage darkening and laying the foundations for grime; artist pages file it as UK garage.')),
 'roll-deep-entourage-terrible': ('2001-12-20','2001 (Reynolds) or 2002','12-inch','Roll Deep Entourage','Terrible','Solid City (per Reynolds)',None,'transition',
   '1d 1d 3d 0d 0d 0d 2s 0d 0d 2s', (TRN,'Grime',None,'Produced by Wiley; Reynolds (2005) pairs it with Know We as garage rap in his Grime Primer. Release year is uncertain.')),
 'pay-as-u-go-champagne-dance-2002': ('2002-04-27','2002 (chart entry 27 Apr 2002)','Single','Pay As U Go','Champagne Dance','So Urban / Sony','6721362','transition',
   '1d 0d 0d 3d 3s 3s 0d 2s 0d 3s', (OUT,'UK garage',None,'The crew\'s party-friendly garage single, recorded with Wiley and Geeneus. Held as an outgroup: the same crew, in its garage mode, in the same year as Eskimo.')),
 'heartless-crew-heartless-theme-2002': ('2002-05-25','2002 (chart entry 25 May 2002)','Single','Heartless Crew','The Heartless Theme (a.k.a. The Superglue Riddim)','East West','HEART02CD','transition',
   '1d 0d 3s 0d 0d 0d 0d 2d 0d 4d', (TRN,'Grime',None,'FACT (2013): too spartan to be called garage, too breezy to qualify as grime. Recorded exactly on the boundary.')),
 # --- producers and instrumentals ---
 'dj-marsta-gridlock-2003': ('2003-06-15','2003','12-inch','DJ Marsta','Gridlock','Total Package Recordings','TPC001','inst',
   '0d 1d 1d 0d 2s 1s 0d 0d 0d 0d', ('Voucher','Grime',None,'Evidence specimen; a white-label instrumental with prominent strings.')),
 'rephlex-grime-2-cat160-2004': ('2004-06-01','2004','Compilation','Kode9, Loefah, Digital Mystikz','Grime 2','Rephlex','CAT 160','dark',
   None, ('Context artefact','Grime',None,'Released as grime in 2004, later described as misidentified grime and proto-dubstep (2010). Evidence of where the boundary between grime and dubstep was drawn, and redrawn.')),
 'dj-target-poltergeist-aim002-2004': ('2004-10-25','2004 or earlier','12-inch','DJ Target','Poltergeist','Aim High Recordings','AIM002','inst',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 0d', ('Voucher','Grime',None,'Evidence specimen; no description of its sound was found, so every code is drafted.')),
 'aftershock-payback-remix-ep-2004': ('2004-11-01','2004','12-inch EP','Various (Aftershock)','Payback (remix EP)','Aftershock',None,'sublow',
   '0d 4d 2d 0d 3d 0s 0d 0d 2d 0d', ('Voucher','Grime',None,'Coded for Terror Danjah\'s Frontline remix; several characters are drafted from descriptions of his style rather than this track.')),
 'low-deep-straight-flush-2005': ('2005-06-01','2005','12-inch','Low Deep','Straight Flush','Colourful State Records',None,'inst',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 0d', ('Voucher','Grime',None,'Evidence specimen; no description of its sound was found, so every code is drafted.')),
 'rebound-x-rhythm-and-gash-2006': ('2006-03-01','2006','12-inch','Rebound X','Rhythm & Gash (Pt. 1)','White label',None,'inst',
   '0d 1d 1d 0d 0d 0d 2s 0s 1d 0s', ('Voucher','Grime',None,'A lyric-free riddim with a traditional eight-bar structure, often cited as a classic.')),
 # --- the 2004-06 wave ---
 'shystie-diamond-in-the-dirt-2004': ('2004-07-12','12 Jul 2004','Album','Shystie','Diamond in the Dirt','Polydor',None,'mc',
   None, ('Context artefact','Grime',None,'Album; reviewed in a 2004 grime round-up. One of the first major-label albums by a woman MC from the scene.')),
 'lady-sovereign-9-to-5-2005': ('2005-08-08','8 Aug 2005','Single','Lady Sovereign','9 to 5','Island','12IS898','mc',
   '2d 4d 2d 0d 3d 0d 1s 2s 0d 3s', ('Voucher','Grime',None,'Evidence specimen at the pop edge of the scene; reviews call it peppy pop with grime roots.')),
 'lethal-bizzle-against-all-oddz-2005': ('2005-08-15','15 Aug 2005','Album','Lethal Bizzle','Against All Oddz','V2',None,'mc',
   None, ('Context artefact','Grime',None,'Album; promoted as grime crossing into rock.')),
 'southside-allstars-southside-2005': ('2005-09-01','2005','Single','Southside Allstars','Southside','Unconfirmed',None,'mc',
   '0d 1d 1d 0d 0d 0d 0d 0d 0d 2d', ('Voucher','Grime',None,'Evidence specimen; South London\'s answer to an East London-centred scene, on Alias\'s Southside Riddim.')),
 'ghetto-2000-and-life-2005': ('2005-10-01','2005','Mixtape','Ghetto (Ghetts)','2000 & Life','Self-released',None,'mc',
   None, ('Context artefact','Grime',None,'Mixtape sold in shops; mixes grime beats with US hip-hop instrumentals.')),
 'roll-deep-shake-a-leg-2005': ('2005-10-10','10 Oct 2005','Single','Roll Deep','Shake a Leg','Relentless','RELCD22','melodic',
   '2d 4d 2d 3d 3d 4d 4s 2d 0d 2d', ('Voucher','Grime',None,'Evidence specimen; a pop single built on a lounge-salsa sample, filed as grime by its album\'s sources and as pop by a 2005 trade review.')),
 'tinchy-stryder-im-back-u-know-2006': ('2006-03-02','2 Mar 2006','Mixtape','Tinchy Stryder','I\'m Back U Know','Boy Better Know',None,'mc',
   None, ('Context artefact','Grime',None,'Mixtape of 17 original productions.')),
 'skepta-duppy-2006': ('2006-05-01','2006 (Stereogum gives 2007)','12-inch','Skepta (with guest MCs)','Duppy','Boy Better Know',None,'mc',
   '0d 4s 2d 0d 0d 0d 0d 0d 0d 2s', ('Voucher','Grime',None,'Evidence specimen; a drum-and-bass-feel riddim with nine MCs trading bars.')),
 'wiley-da-2nd-phaze-2006': ('2006-07-01','1 Jul 2006','Album','Wiley','Da 2nd Phaze','Boy Better Know',None,'eski',
   None, ('Context artefact','Eskibeat',None,'Album placed by XLR8R (2007) in Wiley\'s eski style.')),
 'jme-shh-hut-yuh-muh-2006': ('2006-09-01','2006','Mixtape','JME','Boy Better Know Edition 1: Shh Hut Yuh Muh','Boy Better Know',None,'mc',
   None, ('Context artefact','Grime',None,'Mixtape.')),
}

LANES_EXTRA_FIRST = [('transition', 'Garage transition')]
LANES_EXTRA_LAST = [('inst', 'Riddims and dubs')]

EDGES_NEW = [
 ('pay-as-u-go-know-we-2000', 'roll-deep-entourage-terrible', 'inherit', 'Both produced by Wiley; Reynolds pairs them as chips off the same block'),
 ('pay-as-u-go-know-we-2000', 'pay-as-u-go-champagne-dance-2002', 'inherit', 'Same crew, darker and party modes'),
 ('so-solid-crew-21-seconds-2001', 'so-solid-crew-they-dont-know-album-2001', 'contains', 'Single from the album'),
 ('roll-deep-entourage-terrible', 'danny-weed-creeper', 'inherit', 'Roll Deep, from Entourage to Roll Deep Recordings'),
 ('rephlex-grime-comp-cat156-2004', 'rephlex-grime-2-cat160-2004', 'inherit', 'Sequel compilation on the same label'),
 ('terror-danjah-industry-standard-ep-2004', 'aftershock-payback-remix-ep-2004', 'inherit', 'Same label and producer'),
 ('roll-deep-when-im-ere', 'roll-deep-shake-a-leg-2005', 'inherit', 'Same crew, next single'),
 ('lethal-bizzle-pow-forward-2004', 'lethal-bizzle-against-all-oddz-2005', 'contains', 'Album includes the single'),
]

# Fact-check overrides to first-round specimens (round-2 hardening): field -> new value
OVERRIDE = {
 'danny-weed-creeper': {'date': '2002 (made; release year unconfirmed)',
    'basis': 'A Roll Deep Recordings instrumental (RDR 001), made in 2002, that Risky Roadz recalls Slimzee dropping on Pay As U Go sets; adds the string-led strand to the type series.'},
 'wiley-eskimo-2-devils-mix': {'basis': 'The devil (bass) mix of the sequel Eskimo 2: a version with the drums taken out. Shows how the eski B-side worked as a tool for MCs.'},
 'wiley-eskimo-3-ice-pole': {'label': 'White label (WK007 per one archived listing)'},
 'plasticman-hard-graft-2003': {'artist': 'Mark One vs. Plasticman'},
 'ruff-sqwad-anna': {'label': None},
 'lord-of-the-mics-1-2004': {'artist': 'Jammer and Ratty (creators)'},
 'jammer-murkle-man': {'basis': 'Release details provisional. Jammer says he recorded it after making beats for Wiley; the producer credit is unconfirmed.'},
 'ruff-sqwad-guns-and-roses-vol-1': {'basis': 'Mixtape CD. A 2020 essay places it in the crew\'s sample-led romantic phase, but no source ties specific tracks to samples.'},
 'lady-sovereign-random-2005': {'basis': 'Evidence specimen; Wikipedia tags it grime and hip hop.'},
 'roll-deep-when-im-ere': {'kind': 'Album track (single status disputed)'},
 'ruff-sqwad-died-in-ur-arms': {'basis': 'Evidence specimen; its title and a 2020 essay suggest a sample of Cutting Crew\'s 1986 power ballad, not confirmed by a source.',
    'codes': '0d 1d 1d 0d 3d 0d 4d 3d 1d 0d'},
}
PRODUCER_FIX = {'dizzee-rascal-fix-up-look-sharp': ['Dizzee Rascal']}
DROP_KEYS = {'wiley-morgue'}

# Fact-check overrides to round-2 specimens (h5)
OVERRIDE.update({
 'dj-target-poltergeist-aim002-2004': {'kind': 'Single (format not stated)'},
 'aftershock-payback-remix-ep-2004': {'kind': 'Remix EP (format not stated)'},
 'low-deep-straight-flush-2005': {'date': '2005 (tracklist metadata only)'},
 'lady-sovereign-9-to-5-2005': {'basis': 'Evidence specimen at the pop edge of the scene: one 2006 review calls it peppy pop and contrasts it with her earlier, scatter-mouthed grime.'},
 'lethal-bizzle-against-all-oddz-2005': {'cat': 'JAD1033592', 'label': 'J-DID / V2',
    'basis': 'Album; before release, Reynolds (2005) reported Bizzle promising some grime and rock fusions.'},
 'southside-allstars-southside-2005': {'title': 'Southside Allstars (Southside Riddim)', 'kind': 'Track and video (release format unconfirmed)',
    'basis': 'Evidence specimen; Mixmag says it reflected the south-versus-east tensions in the scene, over Alias\'s Southside Riddim.'},
 'ghetto-2000-and-life-2005': {'date': '2005 (Vice lists it among 2006 mixtapes)', 'label': None,
    'basis': 'Mixtape; Link Up TV says it mixed original beats with US hip-hop instrumentals.'},
 'roll-deep-shake-a-leg-2005': {'basis': 'Evidence specimen; a pop single built on a salsa-quoting sample, filed as pop by a 2005 trade sheet and as grime by sources on its album.'},
 'rebound-x-rhythm-and-gash-2006': {'kind': 'Single or EP track (format not stated)'},
 'skepta-duppy-2006': {'kind': 'Track or single (format not stated)',
    'basis': 'Evidence specimen; a drum-and-bass-feel riddim voiced by a crowd of MCs (sources count eight or nine).'},
 'wiley-da-2nd-phaze-2006': {'of': 'Grime', 'basis': 'Album; Wikipedia tags it grime and eskibeat, but no source checked ties it to the eski style directly, so it is held under grime.'},
})
CALL_DROP = {('dj-target-poltergeist-aim002-2004', 0), ('aftershock-payback-remix-ep-2004', 0)}

# Fact-check overrides to round-2 specimens (h4)
OVERRIDE.update({
 'so-solid-crew-oh-no-dilemma-2000': {'date': '2000 (Hip Hop and R&B Albums chart from 16 Dec 2000)',
    'basis': 'Coded for Dilemma. Kode9 called it ultra-minimal in 2001 (known now through an undated reprint); FACT (2013) calls it a proto-grime flip; the Quietus (2020) calls it a precursor to Pulse X and reports, without a source, that Wiley later said the A-side Oh No started grime. Its producer, Megaman, says the crew still called it garage. A candidate for the start of the grime series, and the clearest test of where the boundary sits.'},
 'pay-as-u-go-know-we-2000': {'basis': 'Produced by Wiley. Simon Reynolds lists it in his Grime Primer for The Wire (dated 2005 on one reposting, 2013 on another); FACT (2013) calls it vanguard grime. Its string hook and MC-first space anticipate Wiley\'s later records.'},
 'roll-deep-entourage-terrible': {'basis': 'Produced by Wiley; Reynolds pairs it with Know We in his Grime Primer. Release year is uncertain.'},
 'so-solid-crew-21-seconds-2001': {'basis': 'A no. 1 garage single at about 140 BPM with each MC taking a short slot (8 bars by Megaman\'s memory, 12 by Wikipedia\'s count). Sources call it garage that helped usher in what became grime. Held as an outgroup whose tempo and MC relay sit close to grime\'s.'},
 'dj-marsta-gridlock-2003': {'basis': 'Evidence specimen; a 12-inch with prominent strings and a vocal B-side.'},
 'shystie-diamond-in-the-dirt-2004': {'basis': 'Album on a major label (Polydor), reviewed in a 2004 grime round-up.'},
})
PRODUCER_FIX['so-solid-crew-oh-no-dilemma-2000'] = ['Megaman (per his Complex interview)']
