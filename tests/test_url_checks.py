import unittest

from src.Model.Checks import (
    analisar_url,
    check_http,
    check_ip,
    check_length,
    check_port,
    check_punycode,
    check_subdomains,
    check_suspicious_terms,
)


class URLRiskScoreTests(unittest.TestCase):
    def test_common_https_url_has_zero_local_risk(self):
        score, reasons = analisar_url("https://example.com")

        self.assertEqual(score, 0)
        self.assertIn("Nenhum indicador de risco", reasons[0])

    def test_http_adds_a_smaller_risk_than_deceptive_indicators(self):
        self.assertEqual(check_http("http://example.com")[0], 10)
        self.assertEqual(check_http("https://example.com")[0], 0)

    def test_ip_address_and_deceptive_url_features_are_scored(self):
        self.assertEqual(check_ip("https://192.0.2.1")[0], 25)
        self.assertEqual(check_ip("https://example.com")[0], 0)

    def test_additional_url_checks_detect_common_signals(self):
        self.assertEqual(check_length("https://example.com/" + "a" * 80)[0], 5)
        self.assertEqual(check_subdomains("https://a.b.c.example.com")[0], 8)
        self.assertEqual(check_punycode("https://xn--e1afmkfd.example")[0], 20)
        self.assertGreater(check_suspicious_terms("https://secure-login.example/verify")[0], 0)
        self.assertEqual(check_port("https://example.com:8443")[0], 10)
        self.assertEqual(check_port("https://example.com:443")[0], 0)
        self.assertEqual(check_port("https://example.com:notaport")[0], 15)

    def test_score_thresholds_match_the_defined_bands(self):
        suspicious_score, _ = analisar_url(
            "http://192.0.2.1:8080/?q=" + "a" * 60
        )
        dangerous_score, _ = analisar_url("http://user@192.0.2.1:8080/")

        self.assertEqual(suspicious_score, 50)
        self.assertEqual(dangerous_score, 70)
        self.assertLessEqual(dangerous_score, 100)

    def test_score_is_capped_at_100(self):
        score, _ = analisar_url(
            "http://user@a.b.c.d.e.f.xn--e1afmkfd.example:8080/"
            + "login/account/verify/"
            + "x" * 210
        )

        self.assertEqual(score, 100)


if __name__ == "__main__":
    unittest.main()
