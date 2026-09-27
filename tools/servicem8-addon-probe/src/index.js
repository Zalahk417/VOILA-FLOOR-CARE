function safeEventSummary(event = {}) {
  return {
    eventName: String(event.eventName || "").toLowerCase(),
    accountUUID: event.auth?.accountUUID || null,
    staffUUID: event.auth?.staffUUID || null,
    jobUUID: event.eventArgs?.jobUUID || event.eventArgs?.entry?.[0]?.uuid || null,
    object: event.eventArgs?.object || null,
    changedFields: event.eventArgs?.entry?.[0]?.changed_fields || []
  };
}

export const handler = async (event) => {
  const summary = safeEventSummary(event);
  console.log(JSON.stringify({
    level: "info",
    message: "bvp-addon-kit-probe",
    ...summary
  }));

  if (summary.eventName === "webhook_subscription") {
    return;
  }

  return {
    eventResponse: `<!doctype html><html><head><meta charset="utf-8"><title>BVP Probe</title></head><body><h1>BVP Addon Kit Probe</h1><p>Action path executed successfully.</p><p>Job: ${summary.jobUUID || "unknown"}</p></body></html>`
  };
};
