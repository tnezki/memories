"""Offline smoke and contract tests. No real student data is read or generated."""
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "app"))
import server


class ScienceToolsFoundationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        (self.workspace / "memories").mkdir()
        (self.workspace / "physics" / "lessons" / "chapter_01").mkdir(parents=True)
        (self.workspace / "physics" / "assessments").mkdir()
        (self.workspace / "physics" / "lessons" / "chapter_01" / "original_cart.html").write_text("<title>Cart</title>")
        (self.workspace / "physics" / "lessons" / "chapter_01" / "sim.css").write_text("body{}")
        (self.workspace / "physics" / "assessments" / "private_teacher.html").write_text("Secret test data")
        (self.workspace / "SCIENCE_Tools").mkdir()
        server.index_resources.cache_clear()
        self.old_workspace = server.workspace_root
        server.workspace_root = lambda: self.workspace
        self.addCleanup(setattr, server, 'workspace_root', self.old_workspace)
        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.url = 'http://127.0.0.1:'+str(self.httpd.server_address[1])

    def request(self, route):
        with urlopen(self.url+route, timeout=3) as response:
            return response.status, response.read(), dict(response.headers)

    def test_health_and_loopback(self):
        status, body, headers = self.request('/health')
        self.assertEqual((status, body), (200, b'SCIENCE_TOOLS_OK_V1'))
        self.assertEqual(headers.get('Cache-Control'), 'no-store')

    def test_read_only_dashboard(self):
        code, html, headers = self.request('/')
        self.assertEqual(code, 200)
        self.assertIn(b'Science Tools', html)
        self.assertIn(b'Content-Security-Policy', str(headers).encode())
        self.assertNotIn(b'Private Data', html)
        code, js, _ = self.request('/app.js')
        self.assertIn(b'Curriculum Library', js)
        self.assertEqual(code, 200)

    def test_status_and_course_registry(self):
        _, b, _ = self.request('/api/status')
        data = json.loads(b)
        self.assertTrue(data['physics_repository_found'])
        self.assertTrue(data['science_tools_folder_found'])
        self.assertEqual(data['public_resource_count'], 1)
        self.assertEqual(data['student_data_connection'], 'not_configured')
        self.assertEqual(data['courses'][0]['planned_instructional_days'],107)

    def test_catalog_sees_only_public_lessons(self):
        _, b, _ = self.request('/api/resources?course=physics&q=cart')
        data=json.loads(b)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['relative_path'], 'chapter_01/original_cart.html')
        _, b2, _ = self.request('/api/resources?course=physics')
        self.assertNotIn(b'private_teacher', b2)

    def test_public_preview_and_path_traversal(self):
        code, b, _ = self.request('/public/lessons/chapter_01/original_cart.html')
        self.assertEqual((code,b),(200,b'<title>Cart</title>'))
        for route in ['/public/lessons/%2e%2e/assessments/private_teacher.html',
                      '/public/lessons/chapter_01/../../../assessments/private_teacher.html',
                      '/public/lessons/chapter_01/original_cart.exe']:
            with self.assertRaises(HTTPError) as cm:
                urlopen(self.url+route)
            self.assertIn(cm.exception.code,(400,404))

    def test_write_blocked(self):
        from urllib.request import Request
        with self.assertRaises(HTTPError) as cm:
            urlopen(Request(self.url+'/api/status',data=b'{}',method='POST'))
        self.assertEqual(cm.exception.code,405)

    def test_shared_ui_assets_bundled(self):
        code, css, _ = self.request('/assets/course-tool.css')
        self.assertEqual(code,200)
        self.assertIn(b'.precision-control',css)
        code, js, _ = self.request('/assets/course-tool.js')
        self.assertEqual(code,200)
        self.assertIn(b'CourseToolUI',js)


if __name__ == '__main__': unittest.main()
