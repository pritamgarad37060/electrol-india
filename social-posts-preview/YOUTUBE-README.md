# Electrol India — standalone YouTube social desk

This is a separate HTML preview and companion server. It does not modify, deploy, or connect to your main election website or account backend.

## Open immediately

Open `electrol-social-posts.html` in a browser. It contains the collected video snapshot. Click a video thumbnail to load the original YouTube player. Internet access is required for images and playback. Private, age-restricted, removed, region-restricted or embedding-disabled videos can fail; use View original.

The directory has 100 politician profiles. Only matched channels have video cards. Other profiles explicitly need a channel link. Matches come from public directory claims or an exact channel title; **this does not establish official ownership**. Review each source and channel before production use. No follower counts, comments or video statistics are invented.

## Automatic updates without viewer login

Install Node.js 20 or newer. Extract this package and double-click `Start-YouTube.cmd`, then open http://127.0.0.1:8125. Keep the server running. It checks matched channel feeds every 15 minutes; the open HTML reads the cached feed every 5 minutes. Refresh starts a cached backend refresh and may initially return the previous snapshot while requests finish. Last successful retrieval is recorded per channel; failed requests keep the preceding snapshot. This is not a guaranteed notification time.

Public feeds contain only a limited number of recent entries. This is not all channel history, nor a guaranteed complete five-day or 30-day archive. Date filters apply to the collected entries. Views and ratings from feeds may be delayed or unavailable. An empty feed is not proof that no uploads exist.

## Extra YouTube information

Enable YouTube Data API v3 in a Google Cloud project and obtain an API key. In PowerShell, run:

```powershell
$env:YOUTUBE_API_KEY = 'YOUR_API_KEY'
node youtube-server.mjs
```

The key stays on the server. Do not paste it into HTML. Restrict it to YouTube Data API and an appropriate server restriction. API calls consume your project's quota.

Select a politician and open About → Load channel details for available subscriber count, public video count, channel views, description, country and creation date. Video details include available duration, definition, captions, view/like/comment counts and live status. Public comments load read-only; disabled comments remain unavailable. Playlists load with pagination. No viewer login is required for these public reads.

Live & upcoming filters API-enriched recent entries. It does not search all channel broadcasts. Shorts are not guessed from duration; the public feed does not provide a reliable Shorts flag. Community Posts are not exposed by the public Data API: the Posts subsection links to the channel's original Posts page.

## Review or add channel mappings

Edit the relevant person's `youtube.channelId` in `youtube-data.json` with a reviewed `UC…` channel ID. Add a public ownership source in `youtube.source`. Restart the server to load changed mappings. For a rebuilt downloadable HTML, run `node build.mjs` from this folder. A channel match and a successful public feed are separate from official account verification.

Local following and bookmarks are saved on this browser/device. Share copies or shares the original video URL. These actions do not like, subscribe, or comment on YouTube. X snapshot features from the previous HTML are retained under X. Instagram/Facebook automatic collection is not configured.

## Files and validation

`youtube-data.json` contains real collected entries with source IDs and retrieval times. `youtube-server.mjs` supplies public feeds and optional API data. `youtube-ui.js` and `youtube.css` are injected by `build.mjs`. `check-youtube.mjs` checks parsing, identities, layouts and interactions using isolated browser fixtures. Fixture checks cannot prove real YouTube playback availability for every visitor.

This local companion binds only to 127.0.0.1. For production, deploy an appropriate backend, configure origin access and server secrets, and review platform display/storage policies. No production deployment has been made.
