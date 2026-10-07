from pathlib import Path
import base64
import io
import json
import os
import re
import shutil
import zipfile

from copy_replacements import (
    GLOBAL_REPLACEMENTS,
    PAGE_REPLACEMENTS,
    SERVICE_PATHS,
    SERVICE_REPLACEMENTS,
)

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
ARCHIVE = HERE / "archive"
CONTENT = HERE / "content"
PARTS = [
    "part-01.b64",
    "part-02.b64",
    "part-03a.b64",
    "part-03b.b64",
    "part-04a.b64",
    "part-04b.b64",
]

PHONE_DISPLAY = "0402 221 071"
PHONE_E164 = "+61402221071"
BRAND = "Voilà Floor Care"
ENQUIRY_URL = "/contact/"
HERO_IMAGE = "/assets/case-studies/tile-grout-restoration-03.webp"


def add_public_phone_details() -> None:
    footer_anchor = '<a href="/contact/">Request a quote</a><a href="/areas/">'
    footer_with_phone = (
        '<a href="/contact/">Request a quote</a>'
        f'<a href="tel:{PHONE_E164}">Call {PHONE_DISPLAY}</a>'
        f'<a href="sms:{PHONE_E164}">Text {PHONE_DISPLAY}</a>'
        '<a href="/areas/">'
    )
    contact_panel = '<div class="info"><h3>Complex jobs are reviewed by a person</h3>'
    contact_panel_with_phone = (
        '<div class="info"><div class="surface"><b>Prefer to call or text?</b><br>'
        f'<a href="tel:{PHONE_E164}">Call {PHONE_DISPLAY}</a> · '
        f'<a href="sms:{PHONE_E164}">Text {PHONE_DISPLAY}</a></div>'
        '<h3>Complex jobs are reviewed by a person</h3>'
    )
    privacy_draft = (
        "Contact details for privacy requests will be published before public launch. "
        "This page is a website implementation draft and must be reviewed against the "
        "final business contact details and systems before production activation."
    )
    privacy_contact = (
        f'For privacy questions, access requests or corrections, call or text '
        f'<a href="tel:{PHONE_E164}">{PHONE_DISPLAY}</a>.'
    )

    replacements = {"footer": 0, "contact": 0, "privacy": 0, "schema": 0}
    html_paths = list(DIST.rglob("*.html"))
    expected_footer_count = 0

    for html_path in html_paths:
        html = html_path.read_text(encoding="utf-8")
        relative_path = html_path.relative_to(DIST).as_posix()
        is_cinematic = relative_path in {"index.html", "cinematic/index.html"}

        if not is_cinematic:
            expected_footer_count += 1
            replacements["footer"] += html.count(footer_anchor)
            html = html.replace(footer_anchor, footer_with_phone)

        replacements["contact"] += html.count(contact_panel)
        replacements["privacy"] += html.count(privacy_draft)
        html = html.replace(contact_panel, contact_panel_with_phone)
        html = html.replace(privacy_draft, privacy_contact)

        if html_path == DIST / "index.html" and not is_cinematic:
            schema_anchor = '"url":"https://www.voilafloor.com.au","areaServed"'
            replacements["schema"] += html.count(schema_anchor)
            html = html.replace(
                schema_anchor,
                f'"url":"https://www.voilafloor.com.au","telephone":"{PHONE_E164}","areaServed"',
            )

        html_path.write_text(html, encoding="utf-8")

    expected = {"footer": expected_footer_count, "contact": 1, "privacy": 1, "schema": 0}
    if replacements != expected:
        raise RuntimeError(f"Phone detail injection mismatch: {replacements} != {expected}")

    site_js = DIST / "assets" / "site.js"
    javascript = site_js.read_text(encoding="utf-8")
    fallback_message = "We could not send that enquiry. Please try again shortly."
    if javascript.count(fallback_message) != 1:
        raise RuntimeError("Enquiry error fallback message was not found exactly once")
    javascript = javascript.replace(
        fallback_message,
        f"We could not send that enquiry. Please call or text {PHONE_DISPLAY}.",
    )

    success_message = "Thanks — your enquiry has been received. We’ll review the details and get back to you."
    if javascript.count(success_message) != 1:
        raise RuntimeError("Enquiry success message was not found exactly once")
    javascript = javascript.replace(
        "status.textContent='" + success_message + "';form.reset()",
        "status.textContent='" + success_message + "'+(out.correlation_id?' Reference: '+out.correlation_id:'');form.reset()",
    )
    javascript = javascript.replace("if(!r.ok)", "if(!r.ok||out.ok!==true||out.captured!==true||!out.correlation_id)")
    javascript = javascript.replace("const data=Object.fromEntries", "form.dataset.submissionId ||= crypto.randomUUID();const data=Object.fromEntries")
    javascript = javascript.replace("JSON.stringify(data)", "JSON.stringify({...data,submission_id:form.dataset.submissionId})")
    javascript = javascript.replace("form.reset()", "form.reset();delete form.dataset.submissionId")
    site_js.write_text(javascript, encoding="utf-8")


def simplify_customer_copy() -> None:
    html_paths = list(DIST.rglob("*.html"))
    pages = {
        html_path.relative_to(DIST).as_posix(): html_path.read_text(encoding="utf-8")
        for html_path in html_paths
    }

    for old, new, minimum_count in GLOBAL_REPLACEMENTS:
        found = sum(html.count(old) for html in pages.values())
        if found < minimum_count:
            raise RuntimeError(
                f"Global copy replacement was found {found} times, expected at least "
                f"{minimum_count}: {old}"
            )
        pages = {path: html.replace(old, new) for path, html in pages.items()}

    for path in SERVICE_PATHS:
        if path not in pages:
            raise RuntimeError(f"Service page is missing from build output: {path}")
        for old, new in SERVICE_REPLACEMENTS:
            if old not in pages[path]:
                raise RuntimeError(f"Service copy was not found in {path}: {old}")
            pages[path] = pages[path].replace(old, new)

    for path, replacements in PAGE_REPLACEMENTS.items():
        if path not in pages:
            raise RuntimeError(f"Copy target page is missing from build output: {path}")
        if path == "index.html" and 'id="house-tour"' in pages[path]:
            continue
        for old, new in replacements:
            if old not in pages[path]:
                raise RuntimeError(f"Page copy was not found in {path}: {old}")
            pages[path] = pages[path].replace(old, new)

    for path, html in pages.items():
        (DIST / path).write_text(html, encoding="utf-8")


def _replace_quote_links(html: str) -> str:
    pattern = re.compile(
        r'<a(?P<before>[^>]*?)href=["\']/contact/?["\'](?P<after>[^>]*)>'
        r'(?P<label>[^<]*(?:quote|Quote|enquiry|Enquiry)[^<]*)</a>'
    )

    def repl(match: re.Match[str]) -> str:
        before = match.group("before")
        after = match.group("after")
        label = match.group("label").strip() or "Request a Quote"
        return f'<a{before}href="{ENQUIRY_URL}"{after}>{label}</a>'

    return pattern.sub(repl, html)


def _site_enhancement_css() -> str:
    return """
<style id="voila-sep11-enhancements">
:root{
  --voila-ink:#17242b;
  --voila-navy:#17384c;
  --voila-ivory:#f7f4ee;
  --voila-copper:#a66f4e;
}
.voila-contact-strip{
  position:relative;z-index:1000;display:flex;justify-content:space-between;
  align-items:center;gap:1rem;padding:.55rem clamp(1rem,4vw,3rem);
  background:var(--voila-ink);color:#fff;font-size:.92rem
}
.voila-contact-strip a{color:#fff;text-decoration:none;font-weight:700}
.voila-contact-strip a:hover{text-decoration:underline}
.voila-hero-banner{
  position:relative;min-height:clamp(430px,58vw,650px);display:grid;
  align-items:end;overflow:hidden;background:var(--voila-ink);color:#fff
}
.voila-hero-banner>img{
  position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center
}
.voila-hero-banner::after{
  content:"";position:absolute;inset:0;
  background:linear-gradient(90deg,rgba(19,31,38,.90) 0%,rgba(19,31,38,.72) 42%,rgba(19,31,38,.18) 100%)
}
.voila-hero-copy{
  position:relative;z-index:2;max-width:760px;padding:clamp(2rem,6vw,5rem);
  text-shadow:0 2px 20px rgba(0,0,0,.2)
}
.voila-eyebrow{font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:.82rem}
.voila-hero-copy h2{font-size:clamp(2.2rem,6vw,5rem);line-height:.96;margin:.5rem 0 1rem}
.voila-hero-copy p{font-size:clamp(1rem,2vw,1.25rem);line-height:1.55;max-width:650px}
.voila-hero-actions{display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;margin-top:1.4rem}
.voila-primary-cta,.voila-secondary-cta{
  display:inline-flex;align-items:center;justify-content:center;min-height:48px;
  padding:.8rem 1.1rem;border-radius:999px;text-decoration:none;font-weight:800
}
.voila-primary-cta{background:#fff;color:var(--voila-ink)}
.voila-secondary-cta{border:1px solid rgba(255,255,255,.65);color:#fff}
.voila-sticky-quote{
  position:fixed;right:1rem;bottom:1rem;z-index:9999;
  display:inline-flex;align-items:center;justify-content:center;
  padding:.85rem 1.1rem;border-radius:999px;background:var(--voila-navy);
  color:#fff!important;text-decoration:none!important;font-weight:800;
  box-shadow:0 12px 28px rgba(0,0,0,.28)
}
.voila-servicem8-button img{display:block;max-width:250px;width:min(250px,70vw);height:auto}
.voila-terms-link{white-space:nowrap}
.card img,.service-card img,.gallery img,[class*="card"] img{
  object-fit:cover;object-position:center
}
@media (max-width:700px){
  .voila-contact-strip{padding:.5rem 1rem;font-size:.82rem}
  .voila-contact-strip span{display:none}
  .voila-hero-banner{min-height:540px}
  .voila-hero-banner::after{
    background:linear-gradient(0deg,rgba(19,31,38,.94) 0%,rgba(19,31,38,.65) 60%,rgba(19,31,38,.18) 100%)
  }
  .voila-hero-copy{padding:2rem 1.25rem}
  .voila-sticky-quote{right:.75rem;bottom:.75rem}
}
</style>
"""


def _write_terms_page() -> None:
    terms_dir = DIST / "terms"
    terms_dir.mkdir(parents=True, exist_ok=True)
    terms_html = f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Terms &amp; Conditions | {BRAND}</title>
<meta name="description" content="Website and service terms for Voilà Floor Care, operated by Midwest Trade Hub Pty Ltd.">
<style>
body{{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#17242b;background:#f7f4ee;line-height:1.65}}
main{{max-width:860px;margin:auto;padding:3rem 1.25rem 5rem}}
a{{color:#17384c}} h1,h2{{line-height:1.15}} .back{{display:inline-block;margin-bottom:2rem}}
.notice{{padding:1rem 1.1rem;background:#fff;border-radius:14px;border:1px solid #ddd6cc}}
</style>
</head>
<body>
<main>
<a class="back" href="/">← Back to {BRAND}</a>
<h1>Terms &amp; Conditions</h1>
<p>These website and service terms apply to {BRAND}, operated by Midwest Trade Hub Pty Ltd. They are intended to be read together with the scope, exclusions, price, timing and any special conditions shown on the customer's quote or booking confirmation.</p>
<h2>Quotes and scope</h2>
<p>Quotes are based on the information and site conditions reasonably available when the work is assessed. If access, measurements, substrate, contamination, pre-existing damage or other material conditions differ from what was understood, any change to scope or price will be discussed before additional work proceeds.</p>
<h2>Deposits and bookings</h2>
<p>Where a quote requires a deposit, the deposit is used to confirm commercial acceptance of the quoted work. A service time is confirmed only when the booking is shown as confirmed by {BRAND}. Acceptance or payment does not authorise an unavailable appointment time.</p>
<h2>Access and customer responsibilities</h2>
<p>Customers should provide safe and reasonable access to the work area and disclose known hazards, fragile items, previous coatings or treatments, staining agents, contamination and other conditions that may affect the service. Any special preparation requirements will be communicated where relevant.</p>
<h2>Results and pre-existing conditions</h2>
<p>Cleaning and restoration can improve many surfaces substantially, but no process can guarantee removal of every stain, odour, wear mark, colour change, coating failure, physical damage or chemical reaction. Permanent or pre-existing conditions may remain. Known limitations will be explained where reasonably identifiable.</p>
<h2>Variations</h2>
<p>Work outside the accepted scope will not be treated as automatically authorised. Material variations should be agreed with the customer before they are performed.</p>
<h2>Rescheduling and cancellation</h2>
<p>Any service-specific cancellation, rescheduling or deposit terms provided on the quote or booking confirmation form part of the agreement. If no specific term is shown, contact us as early as practical so the booking can be reviewed.</p>
<h2>Payment</h2>
<p>The balance and payment timing are those stated on the accepted quote or invoice. Tax invoices and receipts are issued through the business's approved operating systems.</p>
<h2>Website information</h2>
<p>Website content is general information and does not replace an inspection where the floor, fabric, coating, contamination or site condition needs to be identified before a suitable method can be selected.</p>
<h2>Consumer rights</h2>
<p>Nothing in these terms excludes, restricts or modifies rights or remedies that cannot lawfully be excluded under the Australian Consumer Law or other applicable law.</p>
<h2>Privacy</h2>
<p>Personal information is handled in accordance with our <a href="/privacy/">Privacy information</a>. Job photographs are not to be used publicly without an appropriate permission basis.</p>
<div class="notice">
<strong>Contact</strong><br>
Call or text <a href="tel:{PHONE_E164}">{PHONE_DISPLAY}</a> for questions about a quote, booking or service.
</div>
<p><small>Last updated: 11 September 2026.</small></p>
</main>
</body>
</html>"""
    (terms_dir / "index.html").write_text(terms_html, encoding="utf-8")


def apply_latest_site_requirements() -> None:
    _write_terms_page()
    html_paths = list(DIST.rglob("*.html"))

    brand_variants = (
        "Voilá Floor Care",
        "Voila Floor Cleaning & Restoration",
        "Voila Floor Cleaning &amp; Restoration",
        "Voila Floor Care",
        "Voila Floor",
    )

    contact_strip = (
        '<div class="voila-contact-strip">'
        '<span>Geraldton &amp; Mid West floor care</span>'
        f'<a href="tel:{PHONE_E164}" aria-label="Call Voilà Floor Care">{PHONE_DISPLAY}</a>'
        "</div>"
    )
    sticky_quote = (
        f'<a class="voila-sticky-quote" href="{ENQUIRY_URL}" '
        'aria-label="Start a Voilà Floor Care enquiry">'
        "Request a Quote</a>"
    )
    terms_link = '<a class="voila-terms-link" href="/terms/">Terms &amp; Conditions</a>'
    hero = (
        '<section class="voila-hero-banner" aria-label="Tile and grout cleaning in Geraldton">'
        f'<img src="{HERO_IMAGE}" alt="Professionally restored tile and grout floor" '
        'width="1600" height="1000" fetchpriority="high">'
        '<div class="voila-hero-copy">'
        '<div class="voila-eyebrow">Geraldton &amp; Mid West</div>'
        '<h2>Tile &amp; grout cleaning that brings the whole room back to life.</h2>'
        '<p>Deep cleaning and restoration for tired tile and grout, backed by complete floor care '
        'for carpet, upholstery, stone, vinyl, concrete and commercial properties.</p>'
        '<div class="voila-hero-actions">'
        f'<a class="voila-primary-cta" href="{ENQUIRY_URL}">'
        'Start an Enquiry</a>'
        f'<a class="voila-secondary-cta" href="tel:{PHONE_E164}">Call {PHONE_DISPLAY}</a>'
        '</div>'
        '</div></section>'
    )

    for html_path in html_paths:
        html = html_path.read_text(encoding="utf-8")
        relative_path = html_path.relative_to(DIST).as_posix()
        is_cinematic = relative_path in {"index.html", "cinematic/index.html"}

        for variant in brand_variants:
            html = html.replace(variant, BRAND)

        html = _replace_quote_links(html)

        if html_path == DIST / "contact" / "index.html":
            form_count = len(re.findall(r'<form\b[^>]*data-enquiry-form[^>]*>', html))
            if form_count != 1:
                raise RuntimeError("Expected exactly one BVP contact enquiry form")

        if not is_cinematic and "voila-sep11-enhancements" not in html:
            html = html.replace("</head>", _site_enhancement_css() + "</head>", 1)

        if not is_cinematic and '<div class="voila-contact-strip"' not in html:
            body_match = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
            if body_match:
                insert_at = body_match.end()
                html = html[:insert_at] + contact_strip + html[insert_at:]

        if html_path == DIST / "index.html" and not is_cinematic and '<section class="voila-hero-banner"' not in html:
            header_end = re.search(r"</header>", html, flags=re.IGNORECASE)
            if header_end:
                insert_at = header_end.end()
                html = html[:insert_at] + hero + html[insert_at:]
            else:
                body_match = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
                if body_match:
                    insert_at = body_match.end()
                    html = html[:insert_at] + hero + html[insert_at:]

        if "/terms/" not in html and re.search(r"</footer>", html, flags=re.IGNORECASE):
            html = re.sub(
                r"</footer>",
                terms_link + "</footer>",
                html,
                count=1,
                flags=re.IGNORECASE,
            )

        if not is_cinematic and '<a class="voila-sticky-quote"' not in html:
            html = re.sub(
                r"</body>",
                sticky_quote + "</body>",
                html,
                count=1,
                flags=re.IGNORECASE,
            )

        html = html.replace(" — ", " – ")
        html_path.write_text(html, encoding="utf-8")

    index_html = (DIST / "index.html").read_text(encoding="utf-8")
    checks = {
        "canonical brand": BRAND in index_html,
        "House of Voilà hero": 'id="house-tour"' in index_html and 'id="house-film"' in index_html,
        "interactive service hotspots": 'class="hotspot-layer"' in index_html and 'id="scene-services"' in index_html and 'href="/services/carpet-cleaning/"' in index_html,
        "BVP enquiry path": f'href="{ENQUIRY_URL}"' in index_html,
        "no primary ServiceM8 bypass": "book.servicem8.com/request_booking" not in index_html,
        "phone": PHONE_DISPLAY in index_html,
        "terms": "/terms/" in index_html,
        "persistent quote CTA": 'class="floating-cta"' in index_html,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Website acceptance checks failed: {', '.join(failed)}")



def write_bvp_deployment_identity() -> None:
    identity = {
        "schema_version": 1,
        "provider": "cloudflare-pages" if os.getenv("CF_PAGES") == "1" else "local-ci",
        "source_commit": os.getenv("CF_PAGES_COMMIT_SHA") or os.getenv("GITHUB_SHA") or "local",
        "source_branch": os.getenv("CF_PAGES_BRANCH") or os.getenv("GITHUB_REF_NAME") or "local",
        "deployment_url": os.getenv("CF_PAGES_URL") or "",
    }
    (DIST / "bvp-deployment.json").write_text(
        json.dumps(identity, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    payload = "".join((ARCHIVE / name).read_text(encoding="utf-8").strip() for name in PARTS)
    data = base64.b64decode(payload, validate=True)

    root = DIST.resolve()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.infolist():
            target = (DIST / member.filename).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"Unsafe archive path: {member.filename}")
        archive.extractall(DIST)

    if CONTENT.exists():
        shutil.copytree(CONTENT, DIST, dirs_exist_ok=True)

    add_public_phone_details()
    simplify_customer_copy()
    apply_latest_site_requirements()
    write_bvp_deployment_identity()

    # Cinematic surfaces must resolve to real pages, including the rug route.
    home = (DIST / "index.html").read_text(encoding="utf-8")
    for route in set(re.findall(r'href="(/services/[^"]+/)"', home)):
        if not (DIST / route.strip("/") / "index.html").is_file():
            raise RuntimeError(f"Missing cinematic service page: {route}")
    sitemap = DIST / "sitemap.xml"
    xml = sitemap.read_text(encoding="utf-8")
    rug_url = "https://www.voilafloor.com.au/services/rug-cleaning/"
    if rug_url not in xml:
        xml = xml.replace("</urlset>", f"<url><loc>{rug_url}</loc></url>\n</urlset>")
        sitemap.write_text(xml, encoding="utf-8")

    files = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"Voilà Floor Care website built: {files} static files -> {DIST}")


if __name__ == "__main__":
    main()
