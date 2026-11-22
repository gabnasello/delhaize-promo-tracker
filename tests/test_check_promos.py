import unittest

from checker.check_promos import clean_label, parse_price, parse_until


class PromoParsingTests(unittest.TestCase):
    def test_parse_price_with_euros_and_cents(self):
        self.assertEqual(parse_price("Prijs: 3 euro 49 cent"), "3.49")

    def test_parse_price_without_cents(self):
        self.assertEqual(parse_price("Prijs: 3 euro"), "3.00")

    def test_parse_price_returns_empty_for_unknown_format(self):
        self.assertEqual(parse_price("Prijs niet beschikbaar"), "")

    def test_clean_label_removes_promotion_details(self):
        self.assertEqual(
            clean_label("1+1 gratis Promotie enkel geldig met SuperPlus kaart. Bekijk aanbod"),
            "1+1 gratis",
        )

    def test_clean_label_removes_trailing_view_offer(self):
        self.assertEqual(clean_label("-20% Bekijk aanbod"), "-20%")

    def test_parse_until_converts_belgian_date(self):
        self.assertEqual(parse_until("Geldig tot en met 26/11/2026"), "2026-11-26")

    def test_parse_until_returns_empty_without_date(self):
        self.assertEqual(parse_until("1+1 gratis"), "")


if __name__ == "__main__":
    unittest.main()
