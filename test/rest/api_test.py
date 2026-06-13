import http.client
import os
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import pytest

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
DEFAULT_TIMEOUT = 2  # seconds


@pytest.mark.api
class TestApi(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(BASE_URL, "BASE_URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "BASE_URL no configurada")

    def _get(self, path):
        """
        Devuelve (status_code, body_text).
        Si la API responde 400/404..., urlopen lanza HTTPError: lo capturamos.
        """
        url = f"{BASE_URL}{path}"
        try:
            resp = urlopen(url, timeout=DEFAULT_TIMEOUT)
            body = resp.read().decode("utf-8")
            return resp.status, body
        except HTTPError as e:
            body = e.read().decode("utf-8")
            return e.code, body
        except URLError as e:
            self.fail(f"No se pudo conectar a la API en {url}. Error: {e}")

    # ---------- CASOS OK (200) ----------
    def test_api_add_ok(self):
        status, body = self._get("/calc/add/2/2")
        self.assertEqual(status, http.client.OK)
        self.assertEqual(body, "4")

    def test_api_substract_ok(self):
        status, body = self._get("/calc/substract/5/3")
        self.assertEqual(status, http.client.OK)
        self.assertEqual(body, "2")

    def test_api_multiply_ok(self):
        status, body = self._get("/calc/multiply/2/4")
        self.assertEqual(status, http.client.OK)
        self.assertEqual(body, "8")

    def test_api_divide_ok(self):
        status, body = self._get("/calc/divide/8/2")
        self.assertEqual(status, http.client.OK)
        # según tu implementación devuelve "4.0" (float). Lo dejamos tolerante:
        self.assertIn(body, ["4", "4.0"])

    def test_api_power_ok(self):
        status, body = self._get("/calc/power/2/3")
        self.assertEqual(status, http.client.OK)
        self.assertIn(body, ["8", "8.0"])

    def test_api_sqrt_ok(self):
        status, body = self._get("/calc/sqrt/9")
        self.assertEqual(status, http.client.OK)
        # tu API devuelve texto, normalmente "3.0"
        self.assertIn(body, ["3", "3.0"])

    def test_api_log10_ok(self):
        status, body = self._get("/calc/log10/100")
        self.assertEqual(status, http.client.OK)
        self.assertIn(body, ["2", "2.0"])

    # ---------- CASOS KO (400) ----------
    def test_api_divide_by_zero_returns_400(self):
        status, body = self._get("/calc/divide/1/0")
        self.assertEqual(status, http.client.BAD_REQUEST)
        self.assertIn("Division by zero", body)

    def test_api_sqrt_negative_returns_400(self):
        status, body = self._get("/calc/sqrt/-1")
        self.assertEqual(status, http.client.BAD_REQUEST)
        self.assertIn("Square root of negative", body)

    def test_api_log10_zero_returns_400(self):
        status, body = self._get("/calc/log10/0")
        self.assertEqual(status, http.client.BAD_REQUEST)
        self.assertIn("Log10 of zero", body)

    def test_api_non_numeric_returns_400(self):
        status, body = self._get("/calc/add/a/2")
        self.assertEqual(status, http.client.BAD_REQUEST)
        self.assertIn("cannot be converted", body)