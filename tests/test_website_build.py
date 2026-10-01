import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
DIST = WEBSITE / "dist"
SERVICEM8_URL = "https://book.servicem8.com/request_booking?uuid=725f7ba5-b2b6-4997-926c-1f3f26af55eb"


class WebsiteBuildAcceptanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, "build.py"],
            cwd=WEBSITE,
            check=True,
        )

    def test_homepage_has_house_of_voila_and_primary_actions(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn("Voilà Floor Care", html)
        self.assertIn('id="house-tour"', html)
        self.assertIn('id="house-film"', html)
        self.assertIn('class="hotspot-layer"', html)
        self.assertIn('id="welcome-layer"', html)
        self.assertIn('src="/assets/voila-welcome-worker.webp"', html)
        self.assertNotIn('src="data:image/webp;base64,', html)
        self.assertIn('id="scene-services"', html)
        self.assertIn('id="house-lead-form"', html)
        self.assertIn('id="lead-photos"', html)
        self.assertIn('href="/services/carpet-cleaning/"', html)
        self.assertIn('href="/services/upholstery-leather/"', html)
        self.assertIn('href="/services/floor-sealing-finishing/"', html)
        self.assertNotIn('id="service-drawer"', html)
        self.assertIn('data-service="rug"', html)
        self.assertIn('cinematic-timeline.js?v=20261001', html)
        self.assertNotIn('webp""', html)
        self.assertIn('class="hotspot-finger"', html)
        self.assertIn('class="hotspot-finger">☟︎</span>', html)
        self.assertNotIn('poster="/assets/case-studies/tile-grout-restoration-03.webp"', html)
        self.assertNotIn('class="voila-hero-banner"', html)
        self.assertNotIn('class="hotspot-ring"', html)
        self.assertIn("Come in. Let’s look at the surfaces.", html)
        self.assertIn("Show us your surface.", html)
        self.assertIn("Cinematic concept imagery", html)
        self.assertNotIn(SERVICEM8_URL, html)
        self.assertIn("0402 221 071", html)
        self.assertIn('<a class="floating-cta" href="/contact/">Request a Quote</a>', html)
        self.assertIn('/terms/', html)

    def test_cinematic_route_keeps_the_same_interactive_house(self):
        homepage = (DIST / "index.html").read_text(encoding="utf-8")
        cinematic = (DIST / "cinematic" / "index.html").read_text(encoding="utf-8")
        for marker in ('id="house-film"', 'class="hotspot-layer"', 'id="scene-services"', 'id="house-lead-form"'):
            self.assertIn(marker, homepage)
            self.assertIn(marker, cinematic)

    def test_contact_form_uses_bvp_enquiry_endpoint(self):
        contact = (DIST / "contact" / "index.html").read_text(encoding="utf-8")
        javascript = (DIST / "assets" / "site.js").read_text(encoding="utf-8")
        self.assertIn("data-enquiry-form", contact)
        self.assertNotIn(SERVICEM8_URL, contact)
        self.assertIn("/api/enquiry", javascript)
        self.assertIn("out.correlation_id", javascript)
        self.assertIn("Reference:", javascript)

    def test_bvp_deployment_identity_is_emitted(self):
        deployment = json.loads((DIST / "bvp-deployment.json").read_text(encoding="utf-8"))
        self.assertEqual(deployment["schema_version"], 1)
        self.assertIn(deployment["provider"], {"cloudflare-pages", "local-ci"})
        self.assertTrue(deployment["source_commit"])
        self.assertTrue(deployment["source_branch"])

    def test_terms_page_exists_and_preserves_consumer_rights(self):
        terms = (DIST / "terms" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Terms &amp; Conditions", terms)
        self.assertIn("Australian Consumer Law", terms)
        self.assertIn("Midwest Trade Hub Pty Ltd", terms)

    def test_customer_facing_legacy_brand_is_not_on_homepage(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Voilá Floor Care", html)
        self.assertNotIn("Voila Floor Cleaning & Restoration", html)


if __name__ == "__main__":
    unittest.main()
