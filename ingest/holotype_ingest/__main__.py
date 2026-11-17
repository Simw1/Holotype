"""Command line: python3 -m holotype_ingest <command> ...

  index  <files or folders> [--id HT-G###] [--label ...]   add known specimens to the fingerprint index
  scan   <files or folders> [--set] [--transcribe] [--no-stems]
                                                           ingest new audio; long files are treated as sets
  review                                                   write queue/review.html
  decide <sha-prefix> <n> accept|reject [--note ...] [--reviewer ...]
  verify                                                   check the hash-chained ingest log
  status                                                   what is in the index and the queue

Working data lives in --root (default: ./ingest-data).
"""
import argparse
import json
import os
import sys

from . import pipeline, review
from .index import Index


def main(argv=None):
    ap = argparse.ArgumentParser(prog='holotype_ingest', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='ingest-data')
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('index'); a.add_argument('paths', nargs='+'); a.add_argument('--id'); a.add_argument('--label')
    s = sub.add_parser('scan'); s.add_argument('paths', nargs='+'); s.add_argument('--set', action='store_true')
    s.add_argument('--transcribe', action='store_true'); s.add_argument('--no-stems', action='store_true'); s.add_argument('--force', action='store_true')
    sub.add_parser('review')
    d = sub.add_parser('decide'); d.add_argument('sha'); d.add_argument('n', type=int); d.add_argument('verdict', choices=['accept', 'reject'])
    d.add_argument('--note'); d.add_argument('--reviewer')
    sub.add_parser('verify')
    sub.add_parser('status')
    args = ap.parse_args(argv)
    root = args.root
    os.makedirs(root, exist_ok=True)

    if args.cmd == 'index':
        pipeline.index_reference(args.paths, root, ident=args.id, label=args.label)
    elif args.cmd == 'scan':
        pipeline.scan(args.paths, root, {'set': args.set, 'transcribe': args.transcribe, 'stems': not args.no_stems, 'force': args.force})
    elif args.cmd == 'review':
        here = os.path.dirname(os.path.abspath(__file__))
        loci = os.path.join(here, '..', '..', 'data', 'loci.json')
        print(review.render(root, loci))
    elif args.cmd == 'decide':
        p = review.decide(root, args.sha, args.n, args.verdict, args.note, args.reviewer)
        print(f"{args.verdict}: {p['type']} -> {p.get('target')}")
    elif args.cmd == 'verify':
        ok, at = pipeline.verify_log(root)
        print('log intact' if ok else f'log broken at entry {at}')
        sys.exit(0 if ok else 1)
    elif args.cmd == 'status':
        idx = Index(os.path.join(root, 'index'))
        kinds = {}
        for c in idx.catalogue:
            kinds[c['kind']] = kinds.get(c['kind'], 0) + 1
        q = review.load_queue(root)
        print(json.dumps({'index': kinds, 'queue': len(q), 'awaiting': sum(i['status'] != 'reviewed' for i in q)}, indent=1))


if __name__ == '__main__':
    main()
