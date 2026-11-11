"""Compare exact native-coordinate oriented triangle multisets in STL and 3MF.

This is not a general 3MF validator, geometric equivalence test, or print check.
Equality is after float parsing; decimal conversion can round or underflow.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZIP_STORED, ZipFile
import zlib

VERSION = '1.0.0'
UNITS = ('millimeter', 'micron', 'centimeter', 'inch', 'foot', 'meter')
NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
NUMBER = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?')
UNCHECKED = ['3MF schema, package relationships and build references',
             'correctness of the caller-provided source-to-object role pairing',
             'instance and component transforms', 'retriangulated geometric equivalence',
             'topology and manifoldness', 'materials and slicer settings',
             'GUI import, slicing, printing and physical fit']


def _triangle(points):
    points = tuple(points)
    return min(points, points[1:] + points[:1], points[2:] + points[:2])


def _point(values):
    if any(isinstance(value, str) and not NUMBER.fullmatch(value.strip(' \t\r\n'))
           for value in values):
        raise ValueError('invalid decimal coordinate syntax')
    try:
        point = tuple(float(value) for value in values)
    except (ValueError, OverflowError) as exc:
        raise ValueError('invalid coordinate') from exc
    if len(point) != 3 or not all(math.isfinite(value) for value in point):
        raise ValueError('coordinates must be finite triples')
    return point


def _stl(data):
    # Exact binary length is decisive even when its header starts with "solid".
    if len(data) >= 84:
        count = struct.unpack_from('<I', data, 80)[0]
        if len(data) == 84 + 50 * count:
            if not count:
                raise ValueError('empty STL mesh')
            result = Counter()
            for offset in range(84, len(data), 50):
                values = struct.unpack_from('<12fH', data, offset)
                result[_triangle([_point(values[i:i + 3]) for i in (3, 6, 9)])] += 1
            return result
    try:
        lines = data.decode('ascii').splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError('malformed or unsupported STL') from exc
    lines = [line.strip() for line in lines if line.strip()]
    if len(lines) < 2 or not re.fullmatch(r'solid(?:\s+.*)?', lines[0], re.I) or not re.fullmatch(r'endsolid(?:\s+.*)?', lines[-1], re.I):
        raise ValueError('malformed ASCII STL envelope')
    result = Counter()
    i = 1
    while i < len(lines) - 1:
        if i + 6 >= len(lines) - 1:
            raise ValueError('incomplete ASCII STL facet')
        normal = lines[i].split()
        if len(normal) != 5 or [s.lower() for s in normal[:2]] != ['facet', 'normal']:
            raise ValueError('expected facet normal')
        _point(normal[2:])
        if lines[i + 1].lower() != 'outer loop':
            raise ValueError('expected outer loop')
        points = []
        for line in lines[i + 2:i + 5]:
            fields = line.split()
            if len(fields) != 4 or fields[0].lower() != 'vertex':
                raise ValueError('expected vertex')
            points.append(_point(fields[1:]))
        if lines[i + 5].lower() != 'endloop' or lines[i + 6].lower() != 'endfacet':
            raise ValueError('expected endloop and endfacet')
        result[_triangle(points)] += 1
        i += 7
    if not result:
        raise ValueError('empty STL mesh')
    return result


def _project(data, member, object_id, source_unit):
    import io
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            matches = [info for info in archive.infolist() if info.filename == member]
            if len(matches) != 1:
                raise ValueError('selected model member missing or duplicated')
            if matches[0].compress_type not in (ZIP_STORED, ZIP_DEFLATED):
                raise ValueError('unsupported model compression')
            xml = archive.read(matches[0])
    except (BadZipFile, KeyError, RuntimeError, NotImplementedError, zlib.error) as exc:
        raise ValueError('malformed or unsupported 3MF archive') from exc
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ValueError('malformed model XML') from exc
    if root.tag != NS + 'model':
        raise ValueError('unsupported model namespace or root')
    unit = root.get('unit', 'millimeter')
    if unit not in UNITS or unit != source_unit:
        raise ValueError('source and project native units are incompatible')
    resources = root.findall(NS + 'resources')
    if len(resources) != 1:
        raise ValueError('ambiguous model resources')
    objects = resources[0].findall(NS + 'object')
    ids = []
    for obj in objects:
        text = obj.get('id', '')
        if not re.fullmatch(r'[0-9]+', text) or int(text) <= 0:
            raise ValueError('invalid object ID')
        ids.append(int(text))
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate object IDs')
    selected = [obj for obj, oid in zip(objects, ids) if oid == object_id]
    if len(selected) != 1:
        raise ValueError('selected object missing or ambiguous')
    obj = selected[0]
    meshes = obj.findall(NS + 'mesh')
    if len(meshes) != 1 or obj.findall(NS + 'components'):
        raise ValueError('selected object is not one unambiguous mesh')
    vertex_sets = meshes[0].findall(NS + 'vertices')
    triangle_sets = meshes[0].findall(NS + 'triangles')
    if len(vertex_sets) != 1 or len(triangle_sets) != 1:
        raise ValueError('missing or ambiguous mesh arrays')
    try:
        vertices = [_point([v.attrib[k] for k in ('x', 'y', 'z')])
                    for v in vertex_sets[0].findall(NS + 'vertex')]
        result = Counter()
        for face in triangle_sets[0].findall(NS + 'triangle'):
            values = [face.attrib[k] for k in ('v1', 'v2', 'v3')]
            if any(not re.fullmatch(r'[0-9]+', value) for value in values):
                raise ValueError('invalid triangle index')
            indices = [int(value) for value in values]
            if any(index >= len(vertices) for index in indices):
                raise ValueError('triangle index out of range')
            result[_triangle([vertices[index] for index in indices])] += 1
    except KeyError as exc:
        raise ValueError('missing coordinate or triangle index') from exc
    if not result:
        raise ValueError('empty project mesh')
    return result, unit


def audit(source, source_unit, project, object_id, model_part='3D/3dmodel.model'):
    """Return a JSON-serializable audit dict; inputs are paths and object_id is int.

    Status is 通过, 失败, 未执行, or 受阻. No files are written.
    """
    result = {
        'validator': {'name': 'audit_native_mesh', 'version': VERSION},
        'source': {'path': str(source), 'unit': source_unit},
        'project': {'path': str(project), 'model_part': model_part, 'object_id': object_id},
        'frame': 'native coordinates, without transforms',
        'method': 'exact finite Python floats after parsing; decimal conversion may round/underflow; oriented triangle multiset; cyclic rotations only; duplicates retained',
        'unchecked': UNCHECKED,
        'status': '未执行',
        'source_triangles': None, 'project_triangles': None,
        'missing_triangles': None, 'extra_triangles': None,
    }
    try:
        if source_unit not in UNITS or type(object_id) is not int or object_id <= 0:
            raise ValueError('invalid source unit or object ID')
        source_data = Path(source).read_bytes()
        project_data = Path(project).read_bytes()
        result['source']['sha256'] = hashlib.sha256(source_data).hexdigest()
        result['project']['sha256'] = hashlib.sha256(project_data).hexdigest()
        source_faces = _stl(source_data)
        project_faces, unit = _project(project_data, model_part, object_id, source_unit)
        result['project']['unit'] = unit
        missing = sum((source_faces - project_faces).values())
        extra = sum((project_faces - source_faces).values())
        result.update(source_triangles=sum(source_faces.values()),
                      project_triangles=sum(project_faces.values()),
                      missing_triangles=missing, extra_triangles=extra,
                      status='通过' if not missing and not extra else '失败')
    except OSError as exc:
        result.update(status='受阻', reason=str(exc))
    except (ValueError, OverflowError, EOFError) as exc:
        result.update(status='未执行', reason=str(exc))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--source-unit', required=True, choices=UNITS)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--model-part', default='3D/3dmodel.model')
    parser.add_argument('--object-id', required=True, type=int)
    parser.add_argument('--output', type=Path, help='new JSON file; existing files are never overwritten')
    args = parser.parse_args(argv)
    if args.output is not None:
        try:
            if args.output.resolve() in (args.source.resolve(), args.project.resolve()):
                print('Output refused: output aliases an input path', file=sys.stderr)
                return 2
        except (OSError, RuntimeError) as exc:
            print('Output refused: ' + str(exc), file=sys.stderr)
            return 2
    result = audit(args.source, args.source_unit, args.project, args.object_id, args.model_part)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output is None:
        print(text, end='')
    else:
        try:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(text)
        except OSError as exc:
            print('Output refused: ' + str(exc), file=sys.stderr)
            return 2
    return {'通过': 0, '失败': 1}.get(result['status'], 2)


if __name__ == '__main__':
    sys.exit(main())
