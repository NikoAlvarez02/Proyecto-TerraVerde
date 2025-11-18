from django.test import TestCase, Client


class SmokeTest(TestCase):
    def test_true_is_true(self):
        self.assertTrue(True)

    def test_admin_login_page_loads(self):
        client = Client()
        resp = client.get("/admin/login/")
        self.assertEqual(resp.status_code, 200)

