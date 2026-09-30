const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  },
});

const canonicalKeyPayload = (payload) => ({
  source: "website",
  customer_name: payload.customer_name.toLowerCase(),
  email: payload.email.toLowerCase(),
  phone: payload.phone.replace(/\D/g, ""),
  job_address: payload.job_address.toLowerCase(),
  service: payload.service.toLowerCase(),
  message: payload.message.toLowerCase(),
});

async function makeIdempotencyKey(payload) {
  const raw = new TextEncoder().encode(JSON.stringify(canonicalKeyPayload(payload)));
  const digest = await crypto.subtle.digest("SHA-256", raw);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 24);
}

export async function onRequestPost({ request, env }) {
  if (!env.N8N_LEAD_WEBHOOK_URL) {
    return json({ error: "Enquiry service is not configured" }, 503);
  }

  const type = request.headers.get("content-type") || "";
  if (!type.includes("application/json")) {
    return json({ error: "JSON required" }, 415);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid request" }, 400);
  }

  // Honeypot: pretend success so simple bots do not learn the rejection rule.
  if (body.website) return json({ ok: true });

  const clean = (value, max = 2000) => String(value ?? "").trim().slice(0, max);
  const rawAttachments = Array.isArray(body.attachments) ? body.attachments.slice(0, 4) : [];
  let attachmentBytes = 0;
  const attachments = [];
  for (const item of rawAttachments) {
    const name = clean(item?.name, 120);
    const type = clean(item?.type, 80).toLowerCase();
    const size = Number(item?.size || 0);
    const dataUrl = String(item?.data_url || "");
    const allowedType = ["image/jpeg", "image/png", "image/webp"].includes(type);
    const validData = /^data:image\/(jpeg|png|webp);base64,/i.test(dataUrl);
    if (!name || !allowedType || !validData || !Number.isFinite(size) || size <= 0 || size > 3 * 1024 * 1024) {
      return json({ error: "Invalid photo upload" }, 400);
    }
    attachmentBytes += dataUrl.length;
    if (attachmentBytes > 12_000_000) return json({ error: "Photo uploads are too large" }, 413);
    attachments.push({ name, type, size, data_url: dataUrl });
  }
  const payload = {
    source: "website",
    customer_name: clean(body.customer_name, 120),
    phone: clean(body.phone, 60),
    email: clean(body.email, 160),
    job_address: clean(body.job_address, 240),
    service: clean(body.service, 120),
    customer_type: clean(body.customer_type, 80),
    measurements: clean(body.measurements, 160),
    preferred_timing: clean(body.preferred_timing, 160),
    message: clean(body.message, 3000),
    privacy_consent: body.privacy_consent === "yes",
    attachments,
    photo_count: attachments.length,
  };

  if (
    !payload.customer_name ||
    !payload.phone ||
    !payload.job_address ||
    !payload.service ||
    !payload.message ||
    !payload.privacy_consent
  ) {
    return json({ error: "Missing required fields" }, 400);
  }

  const correlationId = crypto.randomUUID();
  const idempotencyKey = await makeIdempotencyKey(payload);
  payload.correlation_id = correlationId;
  payload.idempotency_key = idempotencyKey;

  let upstream;
  try {
    upstream = await fetch(env.N8N_LEAD_WEBHOOK_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-voila-source": "website",
        "x-bvp-correlation-id": correlationId,
        "x-bvp-idempotency-key": idempotencyKey,
      },
      body: JSON.stringify(payload),
    });
  } catch {
    return json({ error: "Enquiry workflow unavailable" }, 502);
  }

  if (!upstream.ok) {
    return json({ error: "Enquiry workflow unavailable" }, 502);
  }

  return json({ ok: true, correlation_id: correlationId });
}

export function onRequest() {
  return json({ error: "Method not allowed" }, 405);
}
