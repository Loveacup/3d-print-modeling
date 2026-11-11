"""Capture/check explicitly selected file identities, not manufacturing validity."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys

VERSION = '1.0.0'
ROLES = {'source', 'parameters', 'export', 'delivery', 'evidence', 'image', 'decision', 'reference'}


def file_path(root, text):
    if not isinstance(text, str) or not text.strip() or any(ord(c) < 32 for c in text):
        raise ValueError('path must be a nonempty file path')
    w = PureWindowsPath(text)
    if '..' in w.parts or w.is_reserved() or any(c in text for c in '*?<>|'):
        raise ValueError('parent traversal, device names and wildcard paths are unsupported')
    if w.drive and not w.root or w.root and not w.drive and not Path(text).is_absolute():
        raise ValueError('ambiguous Windows path')
    if ':' in text[len(w.drive):]:
        raise ValueError('alternate streams are unsupported')
    if w.drive and not Path(text).is_absolute():
        raise ValueError('Windows paths require a Windows host')
    return root / text


def validate(data, root, manifest=False):
    if not isinstance(data, dict) or not isinstance(data.get('revision'), str) or not data['revision'].strip():
        raise ValueError('nonempty revision required')
    entries = data.get('entries')
    if not isinstance(entries, list) or not entries:
        raise ValueError('nonempty entries required')
    ids = set()
    for e in entries:
        if not isinstance(e, dict) or any(not isinstance(e.get(k), str) or not e[k].strip()
                for k in ('id', 'role', 'path', 'version')):
            raise ValueError('each entry requires id, role, path, version strings')
        if e['id'] in ids or e['role'] not in ROLES:
            raise ValueError('duplicate id or unsupported role')
        ids.add(e['id'])
        file_path(root, e['path'])
        links = e.get('relates_to', [])
        if not isinstance(links, list) or any(not isinstance(v, str) for v in links):
            raise ValueError('relates_to must be a list of entry IDs')
    for e in entries:
        if any(v not in ids or v == e['id'] for v in e.get('relates_to', [])):
            raise ValueError('unknown or self-referencing related entry')
    if manifest:
        if type(data.get('schema')) is not int or data['schema'] != 1 or not isinstance(data.get('root'), str):
            raise ValueError('unsupported manifest schema or root')
        for e in entries:
            h = e.get('sha256')
            if h is not None and (not isinstance(h, str) or not re.fullmatch('[0-9a-f]{64}', h)):
                raise ValueError('invalid SHA256')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def observe(path, expected=None, capture=False):
    try:
        current = digest(path)
    except FileNotFoundError:
        return {'sha256': None, 'status': 'missing'}
    except OSError as exc:
        return {'sha256': None, 'status': 'unverified', 'reason': str(exc)}
    status = 'matched' if capture or current == expected else ('unverified' if expected is None else 'changed')
    return {'sha256': current, 'status': status}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['capture', 'verify'])
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--selection', required=True, type=Path)
    p.add_argument('--manifest', required=True, type=Path)
    args = p.parse_args(argv)
    try:
        selection = json.loads(args.selection.read_text(encoding='utf-8-sig'))
        validate(selection, args.root)
        if args.action == 'capture':
            output = file_path(Path.cwd(), str(args.manifest)).resolve()
            inputs = [args.selection.resolve()] + [(args.root / e['path']).resolve() for e in selection['entries']]
            if output in inputs:
                raise ValueError('manifest aliases a selected input or selection file')
            entries = [dict(e, **observe(args.root / e['path'], capture=True)) for e in selection['entries']]
            result = {'schema': 1, 'tool_version': VERSION,
                'captured_at': datetime.now(timezone.utc).isoformat(),
                'root': str(args.root.resolve()), 'revision': selection['revision'], 'entries': entries}
            with args.manifest.open('x', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
            validate(manifest, args.root, manifest=True)
            expected = {e['id']: e for e in manifest['entries']}
            current = {e['id']: e for e in selection['entries']}
            entries = []
            for ident in sorted(expected.keys() | current.keys()):
                old, new = expected.get(ident), current.get(ident)
                if old is None or new is None or any(old.get(k) != new.get(k) for k in
                        ('role', 'path', 'version', 'relates_to')):
                    entries.append({'id': ident, 'status': 'changed', 'reason': 'selection identity changed'})
                else:
                    entries.append(dict(id=ident, **observe(args.root / new['path'], old.get('sha256'))))
            result = {'entries': entries, 'context_matched': manifest['revision'] == selection['revision']
                and manifest['root'] == str(args.root.resolve())}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('context_matched', True) and all(e['status'] == 'matched' for e in result['entries']) else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Identity operation refused: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
