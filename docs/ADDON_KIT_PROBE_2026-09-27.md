# ServiceM8 Addon Kit Probe — 27 Sep 2026

## Scope
Governed test of ServiceM8 Addon Kit 1.3.0 for the Voilà Floor Care / BVP architecture.

Probe branch: `test/addon-kit-probe`

## Results

| Test | Result | Evidence |
|---|---|---|
| Node runtime requirement | PASS | GitHub runner used Node 22.23.2 |
| Addon Kit install | PASS | `@servicem8/addon-kit@1.3.0` installed successfully |
| CLI version | PASS | `addon-kit --version` returned `1.3.0` |
| Synthetic job action handler | PASS | Handler returned expected HTML response |
| Synthetic webhook handler | PASS | `webhook_subscription` event processed without response payload |
| Safe structured logging | PASS | Event metadata logged without access token |
| Manifest/schema validation | PASS | `addon-kit deploy --dry-run` accepted `addon.jsonc` |
| Bundle | PASS | `src/index.js` bundled to 1.9 KB |
| Dry-run deploy | PASS | CLI reported dry run complete; nothing deployed |
| ServiceM8 connected-app read | PASS | VFC tenant readable via connected ServiceM8 app |
| Addon Kit `whoami` in CI | BLOCKED | No `SERVICEM8_API_KEY` or `VFC_SERVICEM8_API_KEY` secret is registered in GitHub Actions |
| Hosted add-on deployment | BLOCKED | Requires Addon Kit authentication |
| Hosted webhook delivery | NOT TESTED | Depends on hosted deployment |
| `addon-kit tail` live log delivery | NOT TESTED | Depends on hosted deployment |
| Slug-based update / rollback behaviour | NOT TESTED | Depends on hosted deployment |

## Hard gate
The repository contained workflow references to `SERVICEM8_API_KEY` / `VFC_SERVICEM8_API_KEY`, but the live Actions runtime resolved both to empty values. The existing ServiceM8 connected app remains healthy; the missing binding is specifically a secret/runtime credential usable by Addon Kit.

Do not copy an existing secret into chat. Resolve this through the governed credential layer or register an authorised full-access ServiceM8 API key as a protected GitHub Actions secret.

## Probe design
The test add-on is read-only. It:
- uses slug `bvp-addon-kit-probe`;
- exposes a safe online Job action named `BVP Probe`;
- subscribes only to Job `status` changes;
- logs event name, account/staff/job identifiers, object and changed fields;
- never logs `auth.accessToken`;
- performs no REST writes.

## Next hosted test once credential binding exists
1. Run `addon-kit whoami`.
2. Deploy the probe.
3. Start `addon-kit tail --format json`.
4. Change one BVP Customer Zero test job status and then restore it.
5. Require a `webhook_subscription` log containing `changedFields:["status"]`.
6. Invoke the Job action manually and require the action execution log plus rendered probe HTML.
7. Redeploy the same slug at v1.1 to prove in-place update behaviour.
8. Remove webhook capability or disable the probe after evidence capture.

## Production decision
Addon Kit 1.3.0 is locally/CI-compatible with the Voilà repository and its manifest/build pipeline. It is **not yet production-certified** for BVP because the authenticated hosted deployment, webhook delivery, live log tail, and update/rollback tests remain unexecuted.
