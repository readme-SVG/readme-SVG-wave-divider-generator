import unittest

from api.index import app


class WaveApiInputParsingTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_wave_handles_invalid_numeric_values_with_defaults(self):
        response = self.client.get(
            "/wave?width=oops&height=nope&amplitude=nanx&frequency=bad&layers=none&opacity=oops&speed=oops"
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('viewBox="0 0 1200 80"', body)

    def test_wave_rejects_invalid_colors_and_uses_safe_defaults(self):
        response = self.client.get(
            "/wave?color_top=not-a-color&color_bottom=xyz&text_color=12&text_stroke_color=%23zzzzzz"
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('fill="#161b22"', body)

    def test_wave_supports_relaxed_boolean_values(self):
        response = self.client.get("/wave?gradient=1&mirror=yes&animate=on")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('<linearGradient id="wg"', body)
        self.assertIn('fill="url(#wg)"', body)
        self.assertIn('<animate attributeName="d"', body)


if __name__ == "__main__":
    unittest.main()
