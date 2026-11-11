import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'audit_native_mesh.py'
spec = importlib.util.spec_from_file_location('audit_native_mesh', SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

A = (0, 0, 0)
B = (2, 0, 0)
C = (2, 2, 0)
D = (0, 2, 0)
CENTER = (1, 1, 0)
FACES = [(A, B, CENTER), (B, C, CENTER), (C, D, CENTER), (D, A, CENTER)]
NAMESPACE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'


def ascii_stl(faces):
    rows = ['solid test']
    for face in faces:
        rows += ['facet normal 0 0 1', 'outer loop']
        rows += ['vertex ' + ' '.join(map(str, point)) for point in face]
        rows += ['endloop', 'endfacet']
    return ('\n'.join(rows + ['endsolid test']) + '\n').encode('ascii')


def binary_stl(faces):
    data = b'solid binary' + b'\0' * (80 - len(b'solid binary'))
    data += struct.pack('<I', len(faces))
    for face in faces:
        data += struct.pack('<12fH', 0, 0, 1, *(x for p in face for x in p), 0)
    return data


def model(faces, unit='millimeter', extra_object='', raw_mesh=None):
    vertices = list(dict.fromkeys(point for face in faces for point in face))
    mesh = '<mesh><vertices>' + ''.join(
        '<vertex x="%s" y="%s" z="%s"/>' % point for point in vertices)
    mesh += '</vertices><triangles>' + ''.join(
        '<triangle v1="%s" v2="%s" v3="%s"/>' % tuple(vertices.index(p) for p in face)
        for face in faces) + '</triangles></mesh>'
    if raw_mesh is not None:
        mesh = raw_mesh
    return (f'<model xmlns="{NAMESPACE}" unit="{unit}"><resources>'
            f'<object id="1">{mesh}</object>{extra_object}</resources></model>').encode()


class NativeMeshAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.stl'
        self.project = self.root / 'project.3mf'
        self.source.write_bytes(ascii_stl(FACES))
        self.write_project(model(FACES))

    def write_project(self, xml, duplicate=False):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.project, 'w') as archive:
                archive.writestr('3D/3dmodel.model', xml)
                if duplicate:
                    archive.writestr('3D/3dmodel.model', xml)

    def run_audit(self, unit='millimeter', object_id=1):
        return audit_module.audit(self.source, unit, self.project, object_id)

    def test_reordered_vertices_faces_and_cyclic_rotations_pass(self):
        faces = [face[1:] + face[:1] for face in reversed(FACES)]
        self.write_project(model(faces))
        result = self.run_audit()
        self.assertEqual(result['status'], '通过')
        self.assertEqual((result['missing_triangles'], result['extra_triangles']), (0, 0))

    def test_dented_interior_point_with_unchanged_bounds_and_count_fails(self):
        top = [(0, 0, 10), (10, 0, 10), (10, 10, 10), (0, 10, 10)]
        bottom = [(x, y, 0) for x, y, _ in top]
        center = (5, 5, 10)
        source_faces = [(top[i], top[(i + 1) % 4], center) for i in range(4)]
        source_faces += [(bottom[0], bottom[2], bottom[1]),
                         (bottom[0], bottom[3], bottom[2])]
        for i in range(4):
            j = (i + 1) % 4
            source_faces += [(bottom[i], bottom[j], top[j]),
                             (bottom[i], top[j], top[i])]
        dent = (5, 5, 9.8)
        changed = [tuple(dent if p == center else p for p in face)
                   for face in source_faces]

        def external_signature(faces):
            points = set(p for face in faces for p in face)
            bounds = tuple((min(p[i] for p in points), max(p[i] for p in points))
                           for i in range(3))
            return bounds, len(points), len(faces)

        self.assertEqual(external_signature(source_faces), external_signature(changed))
        self.source.write_bytes(ascii_stl(source_faces))
        self.write_project(model(changed))
        result = self.run_audit()
        self.assertEqual(result['status'], '失败')
        self.assertEqual((result['source_triangles'], result['project_triangles']), (14, 14))
        self.assertEqual((result['missing_triangles'], result['extra_triangles']), (4, 4))

    def test_reverse_winding_fails(self):
        self.write_project(model([(FACES[0][0], FACES[0][2], FACES[0][1])] + FACES[1:]))
        self.assertEqual(self.run_audit()['status'], '失败')

    def test_missing_and_duplicate_triangles_fail(self):
        for faces in (FACES[:-1], FACES + [FACES[0]]):
            with self.subTest(count=len(faces)):
                self.write_project(model(faces))
                self.assertEqual(self.run_audit()['status'], '失败')

    def test_solid_prefixed_binary_stl(self):
        self.source.write_bytes(binary_stl(FACES))
        self.assertEqual(self.run_audit()['status'], '通过')

    def test_invalid_data_never_passes(self):
        cases = [
            ('malformed_stl', b'solid x\nvertex 0 0 0\nendsolid x', model(FACES), 1, 'millimeter'),
            ('nonfinite_stl', ascii_stl([((float('nan'), 0, 0), B, C)]), model(FACES), 1, 'millimeter'),
            ('empty_stl', ascii_stl([]), model(FACES), 1, 'millimeter'),
            ('malformed_xml', ascii_stl(FACES), b'<model', 1, 'millimeter'),
            ('negative_index', ascii_stl(FACES), model([], raw_mesh='<mesh><vertices><vertex x="0" y="0" z="0"/></vertices><triangles><triangle v1="-1" v2="0" v3="0"/></triangles></mesh>'), 1, 'millimeter'),
            ('out_of_range', ascii_stl(FACES), model([], raw_mesh='<mesh><vertices><vertex x="0" y="0" z="0"/></vertices><triangles><triangle v1="1" v2="0" v3="0"/></triangles></mesh>'), 1, 'millimeter'),
            ('nonfinite_project', ascii_stl(FACES), model([], raw_mesh='<mesh><vertices><vertex x="inf" y="0" z="0"/></vertices><triangles><triangle v1="0" v2="0" v3="0"/></triangles></mesh>'), 1, 'millimeter'),
            ('empty_mesh', ascii_stl(FACES), model([]), 1, 'millimeter'),
            ('component_only', ascii_stl(FACES), model([], raw_mesh='<components><component objectid="2"/></components>'), 1, 'millimeter'),
            ('missing_object', ascii_stl(FACES), model(FACES), 9, 'millimeter'),
            ('duplicate_ids', ascii_stl(FACES), model(FACES, extra_object='<object id="1"/>'), 1, 'millimeter'),
            ('unit_mismatch', ascii_stl(FACES), model(FACES, unit='inch'), 1, 'millimeter'),
        ]
        for name, stl, xml, object_id, unit in cases:
            with self.subTest(name=name):
                self.source.write_bytes(stl)
                self.write_project(xml)
                self.assertEqual(self.run_audit(unit, object_id)['status'], '未执行')

    def test_duplicate_selected_member_rejected(self):
        self.write_project(model(FACES), duplicate=True)
        self.assertEqual(self.run_audit()['status'], '未执行')

    def test_missing_input_is_blocked(self):
        result = audit_module.audit(self.root / 'missing.stl', 'millimeter', self.project, 1)
        self.assertEqual(result['status'], '受阻')

    def test_rejects_underscore_numeric_tokens(self):
        self.source.write_bytes(ascii_stl(FACES).replace(b'vertex 0 0 0',
                                                       b'vertex 0_0 0 0', 1))
        self.assertEqual(self.run_audit()['status'], '未执行')
        self.source.write_bytes(ascii_stl(FACES))
        self.write_project(model(FACES).replace(b'x="0"', b'x="0_0"', 1))
        self.assertEqual(self.run_audit()['status'], '未执行')

    def test_rejects_corrupt_deflate_as_unperformed(self):
        with zipfile.ZipFile(self.project, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('3D/3dmodel.model', model(FACES))
            info = z.getinfo('3D/3dmodel.model')
        data = bytearray(self.project.read_bytes())
        name_len, extra_len = struct.unpack_from('<HH', data, info.header_offset + 26)
        offset = info.header_offset + 30 + name_len + extra_len
        data[offset] = (data[offset] & 0xf8) | 0x07
        self.project.write_bytes(data)
        self.assertEqual(self.run_audit()['status'], '未执行')

    def test_unsupported_zip_compression_is_unperformed(self):
        with zipfile.ZipFile(self.project, 'w', compression=zipfile.ZIP_BZIP2) as z:
            z.writestr('3D/3dmodel.model', model(FACES))
        self.assertEqual(self.run_audit()['status'], '未执行')

    def test_rejects_output_alias_of_missing_input(self):
        missing = self.root / 'missing.stl'
        completed = subprocess.run([sys.executable, str(SCRIPT), '--source', str(missing),
                                    '--source-unit', 'millimeter', '--project', str(self.project),
                                    '--object-id', '1', '--output', str(missing)],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(missing.exists())

    def test_cli_refuses_overwrite_preserving_sentinel(self):
        output = self.root / 'sentinel.json'
        output.write_text('sentinel', encoding='utf-8')
        completed = subprocess.run([sys.executable, str(SCRIPT), '--source', str(self.source),
                                    '--source-unit', 'millimeter', '--project', str(self.project),
                                    '--object-id', '1', '--output', str(output)],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(output.read_text(encoding='utf-8'), 'sentinel')


if __name__ == '__main__':
    unittest.main()
