# Electrol India.Com — supplied HTML with connected backend

`index.html` is **claude final html project file.html**, preserved byte-for-byte apart from three script attachments. Its CSS, layout, menus, comparison builder, charts, sheets, result views, profile screens and native navigation remain authoritative.

The previous replacement frontend (integration.js, services.js, account frontend modules and their styles) has been removed from the active project. A local .ui-rollback backup is excluded from deployment. The original india-elections website has not been replaced or deployed.

## Run

Double-click **Start-Website.cmd**, then open the printed address. Port 8100 is preferred; another project's preview on that port makes the server try the next available port. A matching running copy is reused. Restart the server after changing source HTML.

Requires Node.js 22+. There are no runtime npm dependencies.

## Files

- index.html: the supplied frontend and its original view logic.
- js/backend-guard.js: blocks simulated account saving/sign-in if the connection attachment cannot load.
- js/backend-bridge.js: connects the HTML's controls to the account API, using its existing forms, sheets and visual components. No previous account frontend or CSS is loaded.
- js/html-data.js: connects the existing election/comparison views to project records. The existing builder, tabs, charts, maps and result sheets remain. Missing records do not receive generated candidate figures.
- netlify/functions and netlify/lib: Supabase account API, correction handling, notification delivery and server security.
- data: public project records, including 46 parliamentary/Assembly editions and local-body imports. The compact local-body index does not duplicate the candidate database.
- tools/prepare-html.mjs: extracts the original inline script/style contents without rewriting them, so generated SEO pages share cached assets instead of containing the full 2.85 MB source. This changes packaging, not the UI.

News remains the standalone section supplied in the HTML. Its explainers/example content is not represented as a connected live newsroom. Language controls remain as supplied. Home-calendar and schedule-watchlist presentation has been removed for the later release requested by the user.

## Accounts

The original sign-in, signup, email-code, recovery, profile-editing, Follow, saved comparison/profile, notification preference and correction controls use /api/account/ endpoints. Private session tokens remain in server-managed cookies. Device display preferences remain local.

Connected modules support profile media, password changes, authenticator enrollment and verification, sessions, connected identities, export and deletion. Sensitive operations use confirmation in the HTML's own sheet/form styles. Google sign-in retains the original view context when returning. Unconfigured providers remain unavailable.

Correction reports have owner-scoped database policies. Existing election/account tables were preserved.

## Verification

- Removing the three attachments from index.html reproduces the supplied HTML exactly.
- Home hero DOM/dimensions match the reference. Menus, comparison builder and result sheets retain their original structure.
- Internal navigation retains the HTML's behavior instead of forcing the previous replacement's URLs.
- Browser checks cover original-form login, Follow/Unfollow reload persistence using isolated fixtures, real-data comparisons, and reference-layout checks at 320, 393, 768 and 1440 px in light/dark modes.
- Real provider tests used disposable confirmed accounts to verify password login, two-session Follow persistence, account isolation, profile saving, correction submission/isolation, session revocation, authenticator enrollment/challenge/verification/removal, export and test-account deletion. Disposable accounts were cleaned up; no email was sent.
- Transport/security checks cover cookies, CSRF, invalid payloads, private data boundaries and provider failures.

Commands: npm run check, npm run check:account, npm run check:startup, npm run check:browser and npm run check:connection. Browser checks use the host's installed Playwright runtime. The optional npm run check:account:live creates and cleans up disposable accounts in the configured backend.

## Remaining limits

Run `Finish-Connection.cmd` from the complete imported project to check the configured backend, upload changed public datasets by their unique path, and verify every local checksum. It stops on a failed step and leaves account tables and private configuration untouched. An empty Supabase dataset table cannot be used for a successful `data:pull`; import with `data:push` first.

Interactive Google consent, actual email/OTP delivery and delivered browser push require real-user/device testing. Enabled settings and successful cryptography tests do not establish actual delivery.

Local rosters can be partial. Rural division candidate records, Gram Panchayat/Sarpanch results, Council counting rounds and compatible historical boundaries remain incomplete. Missing values are unavailable. Existing imports are not all independently reconciled against final official sheets.

The supplied HTML itself has some narrow-screen decorative overflow. Parity checks verify that the connection introduces no additional overflow; they do not redesign the reference. Not every reference option or legacy URL is certified for production.

## Release

npm run build produces dist with shared original assets, route metadata, sitemap and no-JavaScript result tables. Netlify configuration includes account routes and notification schedules. No deployment was performed.

.env.local contains private server configuration. It must not be served or shared as a public asset. Configure production credentials, origin, callbacks, email and push settings before publishing.
The supplied HTML's Pune and Mumbai 2017 snapshots remain authoritative for those comparison views; partial raw imports are not mixed into their totals. Missing candidate vote counts remain unavailable.

## Connected photos and state maps

All 540 original MP photographs are copied under data/photos and matched by MP ID, with a local-first profile image and remote fallback. Directory thumbnails use the same IDs. State maps lazy-load the seven GeoJSON files plus Maharashtra's existing constituency paths; exact constituency-number joins are checked before rendering. Available editions are Assam 2026, Bihar 2025, Kerala 2026, Puducherry 2026, Tamil Nadu 2026, Uttar Pradesh 2022, West Bengal 2026 and Maharashtra from 2009. Earlier boundaries are not inferred. Andhra Pradesh's supplied compact geometry contains parliamentary regions and is not used as assembly boundaries. The existing Lok Sabha geographic map remains connected. Photos and geometry remain static project files and do not require another Supabase JSON upload. Run npm run check:media for local photo hashes, identity coverage and browser map checks.

The profile adapter also joins all 540 supplied MP IDs to their 2024 winning result profiles using source names, matched constituencies and dated election histories. Three seats have no supplied biography/photo record. It does not assign a winning MP's photo to other candidates or Assembly representatives. Available Facebook, X and Instagram links appear with the existing social icons; absent handles are not invented. Map hover cards share the original styling and stay inside the visible viewport, with keyboard focus and Escape support. Run npm run check:hover to verify photo aliases, source social URLs and both map hover cards.

## Project folders

| Path | Purpose |
| --- | --- |
| index.html, js/, css/ | Frontend and generated browser assets |
| assets/, data/ | Public media and election records, served at stable URLs |
| src/shell.html, dist/ | Generated shell and publish output |
| netlify/, supabase/ | Server functions, search index, SQL and migration history |
| tools/ | Build, development, verification and data maintenance commands |
| docs/ | Project reference material, including the implementation inventory |
| reports/, scratch/ | QA evidence, source snapshots and scratch rollback files |
| tmp/ | Maintenance inputs and temporary outputs. Some Parliament imports read this path |
| social-posts-preview/ | Standalone social and YouTube preview project |

Scratch snapshots from the audit and label fixes are under scratch/rollback/. The separate UI and data connection recovery directories retain their original paths.
