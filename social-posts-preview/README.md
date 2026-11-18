# Electrol India — Social desk

Open **electrol-social-posts.html** directly in a browser. It is one self-contained HTML file with inline styling, scripts, 100 representative records and embedded portraits. Internet access is only needed for external links, the optional X timeline, and media in imported posts.

## Added: five-day post embeds

The default News view now contains **10 individually sourced X post URLs**, one each for Narendra Modi, Rahul Gandhi, Amit Shah, Rajnath Singh, Shashi Tharoor, Priyanka Gandhi Vadra, Dharmendra Pradhan, Piyush Goyal, S. Jaishankar and Om Birla. The same cards appear on their profiles.

The fixed snapshot covers **27–31 October 2026 in India**. This is a selected snapshot, not all posts from these accounts. Post IDs and attribution were located in dated government releases, news reports and an independent archive. Dates were cross-checked against the timestamps encoded in X post IDs. The individual post embed loads directly from X when its card approaches the viewport. No copied post text or made-up engagement counts are used. If X declines to render a post, its exact original URL and the source that linked it remain visible.

Direct X requests returned access errors during collection, so current post availability, ownership and live playback were not independently verified. “Sources & coverage” in the HTML lists the provenance and this limitation for each link. This file does not automatically discover new post links; its snapshot remains dated when opened later. The original 100-account directory remains available. The focus roster adds Piyush Goyal and S. Jaishankar and uses Om Birla's handle as linked by the Lok Sabha Secretariat.

The link selection is stored in **embeds-five-days.json** and embedded inside the standalone HTML at build time. No API key is needed to request these official individual-post widgets.

## What is ready

- Mobile-first design based on your reference, with a desktop sidebar and responsive reading width.
- Light, dark and system themes; follows and bookmarks saved on the current device.
- 100 distinct X handles from your existing Lok Sabha parliamentary biographies. Selection is balanced across the recorded states, with several familiar profiles first. The Rajya Sabha biographies currently have no recorded X handles, so none were guessed.
- Representative profiles, biography details, the combined feed, search, party/state/person filters, chronological sorting, pagination, source links, and per-account coverage.
- Import JSON through Settings; only valid, member-matched public post links are accepted.
- The default News view automatically requests the selected representative's public X timeline, with a 100-account selector. Profiles also open their X timeline automatically when no archive is imported. If X blocks the embed, a clear message and “Read posts on X” link appear. The separate 30-day archive tab remains available for imported data.

## What is NOT included yet

**No complete X post archive was downloaded:** an X API token is not configured. The file has the selected 10 post URLs above; the separate 30-day archive is still “not imported”. Live post content and timelines are supplied by X rather than stored in the file; X can require login or decline to render them. Missing data is never presented as zero activity. Account ownership has not been independently rechecked against X.

The HTML currently concentrates on X. Instagram, Facebook and YouTube feeds are not connected; they do not have misleading working-looking filters.

## Import the previous 30 days

Requires Node.js 22+, an X developer app with permission for `GET /2/tweets/search/all`, and sufficient credits. X API requests can incur charges. Review your account's rates and spending limit first. The importer never asks for payment or purchases credits. Keep the token out of HTML and source control.

From PowerShell, in this folder, set your token for the current terminal only:

```powershell
$env:X_BEARER_TOKEN = Read-Host 'Enter your X API bearer token' -MaskInput
node import-x.mjs
```

The default attempts all 100 accounts, up to 50 pages of 100 posts per account. To check access with a small initial request:

```powershell
node import-x.mjs --limit 1 --max-pages 1
```

Then run the full import when ready. It generates **posts.json** and rebuilds the HTML. If a page cap, rate limit or service error interrupts an account, it is labeled partial or unavailable. Access/billing/rate-limit failures stop the remaining accounts rather than retrying and silently spending more. Increase the page cap explicitly if needed:

```powershell
node import-x.mjs --max-pages 100
```

The period is a rolling 30 days ending 30 seconds before the import begins, using UTC instants. Every account in one import uses the same boundaries. The app displays that import window rather than relabeling an older archive as current. Posts have exclusive end dates. Pagination uses X's returned cursor and accounts are matched by the numeric ID returned for the recorded handle. Replies and quotes are retained and labeled when identified in the source.

“Complete” means pagination of **the public records returned by X** finished. Deleted, protected, withheld or unindexed content, and repost completeness, cannot be guaranteed. A blank response or a failed request is not proof of no political activity. Old archives need another import to refresh.

## Optional local server

```powershell
node serve.mjs
```

Open http://127.0.0.1:8125/. This server only exposes the HTML, never API tokens, source files or your website configuration.

## Website and updates

This is a separate preview. Your existing website pages, backend and URLs were not modified. To deploy the final file, serve it as a standalone page or integrate its views with your existing navigation. No deployment or scheduling was performed.

Source profiles are retained for provenance. The generated roster excludes contact addresses, phone numbers and emails. The importer reads the token only from its environment and sends it only to https://api.x.com, with redirects refused. No token field exists in the browser.

## Official references

- https://docs.x.com/x-api/posts/search-all-posts
- https://docs.x.com/x-api/users/get-posts
- https://help.x.com/en/using-x/embed-x-feed

## Regenerate and validate

The generator refreshes profiles from the existing website's data folder when available. The download also includes the selected roster, so it can rebuild independently:

```powershell
node build.mjs
node check.mjs
```

The delivered HTML remains portable without those source files. Standalone imported JSON can be loaded through Settings even without regenerating.
