import { handler } from "../src/index.js";

const action = await handler({
  eventVersion: "1.0",
  eventName: "bvp_probe",
  auth: { accountUUID: "synthetic-account", staffUUID: "synthetic-staff", accessToken: "DO_NOT_LOG" },
  eventArgs: { jobUUID: "synthetic-job" }
});
if (!action?.eventResponse?.includes("Action path executed successfully")) {
  throw new Error("Action handler did not return expected HTML");
}

const webhook = await handler({
  eventVersion: "1.0",
  eventName: "webhook_subscription",
  auth: { accountUUID: "synthetic-account", staffUUID: "synthetic-staff", accessToken: "DO_NOT_LOG" },
  eventArgs: {
    object: "job",
    entry: [{ uuid: "synthetic-job", changed_fields: ["status"], time: "2026-09-27 00:00:00" }]
  }
});
if (webhook !== undefined) {
  throw new Error("Webhook handler should complete without response payload");
}

console.log(JSON.stringify({ok:true, action:true, webhook:true}));
