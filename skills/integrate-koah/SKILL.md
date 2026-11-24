---
name: integrate-koah
description: Install Koah's Ad SDK (publishers monetizing AI apps with native ads) or Koah Conversion Tracking — the browser pixel, the server-side Conversion API, or both (advertisers measuring event ROI). Triggers on "Koah", "koahlabs", "koah.ai", "monetize an AI app", "native ads", "ad placement", "sponsored content", "track conversions", "install a pixel", "conversion API", "CAPI", "server-side conversion tracking".
---

# Koah integration

This skill helps install Koah, an ad network for AI applications. Koah ships two products, and each has its own section below:

1. **Ad SDK** - publishers show native ads in their app, with the iOS, Android, Flutter, React Native, or JavaScript SDK. See [Ad SDK: show ads in an app](#ad-sdk-show-ads-in-an-app).
2. **Conversion Tracking** - advertisers report visitor actions to Koah to measure ROI. Two reporting methods, usable separately or together: the **pixel** (a JavaScript snippet that reports from the visitor's browser) and the **Conversion API** (a REST endpoint your server posts to). See [Conversion Tracking: measure conversions](#conversion-tracking-measure-conversions).

Before you write any code, read the docs sitemap: https://docs.koahlabs.com/llms.txt. It lists every docs page with a one-line description. Use it to find the pages that this skill names.

## Pick the product

If the user's intent is ambiguous, ask:

> "Are you monetizing an app with ads (Ad SDK), or measuring conversions and events on your site (Conversion Tracking)?"

Strong cues for **Ad SDK**:

- AI chatbot or assistant project, or the codebase has a chat UI
- User mentions "monetize", "revenue", "ads", "show ads"
- Mobile project structure: `Podfile`, `build.gradle`, `pubspec.yaml`, or `app.json` present
- React Native / Expo project

Strong cues for **Conversion Tracking**:

- Marketing site or landing page
- User mentions "pixel", "track conversions", "events", "ROI", "campaign performance"
- Next.js / Webflow / Framer project, or a static HTML site
- User identifies as an advertiser, not a developer
- User mentions server-side tracking, CAPI, ad blockers, or cookie/consent limits

If you have strong evidence for one, skip the question and go to that product's section.

## Rules for every integration

- **Ask the user** for their publisher ID (Ad SDK) or advertiser ID (Conversion Tracking) if you don't see one in the codebase. Direct links to the Koah dashboard:
  - Publisher ID: https://app.koahlabs.com/publisher/settings?tab=integration
  - Advertiser ID: https://app.koahlabs.com/advertiser/settings?tab=brand
  - API keys (Conversion API): https://app.koahlabs.com/advertiser/settings?tab=api_keys
- Do **not** leave placeholders like `YOUR_ADVERTISER_ID` or `YOUR_PUBLISHER_ID` in the code you write unless the user explicitly asks you to - these placeholders **will not** work.
- **Never invent** SDK APIs, component names, event names, configuration options, or install commands. Check each one against the docs before you write code.
- Do not claim an integration is complete until you have done its verification steps.

## Ad SDK: show ads in an app

For publishers who show Koah ads in their app.

### Step 1 - Identify the framework

Prefer evidence from the project over asking:

- `Podfile` or `Package.swift` -> **iOS** (Swift)
- `build.gradle` or `settings.gradle.kts` -> **Android** (Kotlin)
- `pubspec.yaml` -> **Flutter** (Dart)
- `app.json` + `react-native` in `package.json` -> **React Native** (TypeScript)
- `react` in `package.json` (no React Native) -> **JavaScript** (the script-tag SDK works in React — gate `requestAd` on `window.koah` and pass a ref'd element as `target`)
- HTML files with raw `<script>` tags, no framework -> **JavaScript** (vanilla)

If still unclear, ask: *"Which framework is your app - iOS (Swift), Android (Kotlin), Flutter, React Native, React (web), or vanilla JavaScript?"*

### Step 2 - Find the install page

In `llms.txt`, find the overview page for the framework and follow its install steps exactly.

- All four mobile SDKs have a stable 1.0 release. Use the stable install steps. For a beta integration, replace the prerelease dependency pin with the stable version.
- If the project already uses Koah 0.x, follow the platform's migration guide instead of a fresh install. 1.0 is a breaking release.
- On the web, code that calls `process()`, `processStaticAd()` or `generateTextAd()` serves no ads. Follow the JavaScript migration guide to move it to `requestAd()`.
- For theming, sizing, and other deeper topics, find the page in `llms.txt`.

### Step 3 - Install minimally, then customize

Each SDK overview page has a minimal example. Run that example first with a demo publisher key. Check that the SDK loads and shows an ad. Then add the developer's queries, conversation IDs, theming and analytics tags.

### Step 4 - Make the ad look like part of the chat

Apply these rules on every platform. An ad that does not match the app gets fewer clicks, and users read it as an intrusion.

**Request an ad for every response.**

- Call the SDK once for each assistant response, after the response finishes streaming. The request needs the full answer as context.
- Do not limit how often you request ads. Do not add a frequency cap, a random sample, an "every Nth message" rule, or a minimum message count.
- The fill rate is not set in client code. The publisher sets it with Koah, and Koah decides on the server whether each request gets an ad. A request without an ad shows nothing.
- Give each response its own slot: its own `cacheKey` on mobile, and its own `target` element on the web.
- Do not add a fixed wait, such as `setTimeout`, `sleep`, a timer, or a polling loop, to wait for the SDK, the response, or the ad. Wait for the real signal instead: the end of the response stream, the SDK script's `load` event on the web, and the result of the ad request. A fixed wait fails on a slow device and delays the ad on a fast one.

**Match the typography of the AI response.**

- Make the ad's font the same as the font of the assistant's response text. Every SDK uses the host app's font by default. On the web, the default `fontFamily: 'inherit'` takes the font at the slot's position in the page. If the response text uses a different font, set the theme font to it: `fontFamily` on the web, Android, Flutter, and React Native, and `font` on iOS.
- On the web, do not put the slot inside a container whose CSS rules restyle descendant elements, such as markdown or `prose` styles for `p`, `strong`, `a`, or `button`. Those rules reach the ad's text. Put the slot next to the response, not inside it.
- Change the ad's type only through the theme font. Do not target the ad's inner elements.

**Match the color scheme.**

- Set `colorScheme` to follow the app's light and dark mode. Do not fix it to one mode when the app has both.
- Keep the default card chrome. Do not switch to the borderless chrome unless the user asks for it.
- The card paints its own surface color for the light or dark scheme. On the web, when the chat has a branded background, set the card's colors to the app's own color tokens on `[data-koah="root"]`, with `!important`: `--koah-color-surface` (the chat background), `--koah-color-border`, `--koah-color-text-primary`, and `--koah-color-text-secondary`. Follow the app's light and dark mode, for example with `var(--background)`.

**Do not change the ad unit.**

- Render the Koah component as it is. Do not add anything inside it or around it: no border, shadow, background, padding, header, divider, close button, or "Ad" or "Sponsored" label. The ad already shows its own disclosure and menu.
- Do not cover, clip, crop, scale, or transform the ad. Do not hide parts of it. Do not target its inner elements with CSS selectors.
- Change the ad's look only with the documented theme settings and sizing parameters.

**Place the ad below its response.**

- Show the ad below the response it belongs to. Do not insert it above text that the user is reading.
- Do not reserve an empty box before the ad loads. A request without an ad must leave no gap.
- Do not scroll the conversation to bring the ad into view.

### Step 5 - Verify

- A `KoahCard` (or platform equivalent) renders without errors.
- At least one ad displays in the test environment.
- Every assistant response sends one ad request. Count the requests in the logs, or in the browser's Network tab on the web.
- The ad's body text has the same font family and weight as the response's body text.
- Nothing is added around the ad.
- On a mobile SDK, set `logLevel` to debug. On the web SDK, open the browser console and look for messages with the prefix `[KOAH]`.
- On the web SDK, confirm in the Network tab that the `https://app.koah.ai/js` request succeeds and that `window.koah` is defined in the console. If the request is blocked or fails, see the ad blocker gotcha below.

### Ad SDK gotchas

- **Demo keys**: never ship a demo publisher ID to production. Replace with a real one before launch.
- **Ad blockers stop the web SDK during testing**: ad blockers and browser content blockers can block the requests to `app.koah.ai`. Some browsers block ads by default with no extension installed, such as Dia, Arc, and Brave (Shields). Safari content blockers can block them too. A blocked request shows as blocked or failed in the Network tab, `window.koah` stays undefined, and no ad request goes out. If the `app.koah.ai` requests fail in the user's browser, tell the user to turn off the ad blocker or the browser's built-in ad blocking for their development site. This is not a bug in the integration.
- **`window.koah` is undefined after the SDK script loaded**: the script is `async`, so `window.koah` is undefined until it finishes. Wait for the script's `load` event before you judge. If the script loaded and `window.koah` is still undefined, Koah did not accept the publisher ID in the `token` parameter. Check the ID against the dashboard. If it matches, ask the user to contact Koah, because the publisher account may not be active.
- **iOS / SPM vs CocoaPods**: Koah ships as a Swift Package - don't try to install via CocoaPods. If the project uses CocoaPods for everything else, add Koah as an SPM dependency separately.
- **React Native / Expo**: Koah works with both bare RN and Expo (managed workflow), but the install steps differ. Confirm which one before following the page.

## Conversion Tracking: measure conversions

For advertisers who report visitor actions to Koah.

### Step 1 - Choose the reporting method and install path

First, the **reporting method**. If the user hasn't said, ask:

> "Do you want the browser pixel (quickest, but misses visitors with ad blockers or analytics disabled), the server-side Conversion API (more reliable, needs backend code), or both?"

Cues for **pixel**: no backend to change, a site builder (Webflow/Framer), a tag manager, or the user isn't a developer.
Cues for **Conversion API**: an existing server they control, a CSP or security policy against third-party scripts, or a stated concern about ad blockers and tracking reliability.
Cues for **both**: the user wants maximum coverage. Both is the most accurate option and the most work — it requires shared event IDs, see Step 2.

Then the **install path**:

- Pixel, site managed via Webflow -> **Webflow**
- Pixel, site built in Framer -> **Framer**
- Pixel, Google Tag Manager container present in HTML -> **Google Tag Manager**
- Pixel, otherwise -> **Manual pixel** (raw JS snippet)
- Conversion API -> **Manual API installation** (backend code; the GTM path for the API is not shipped yet)

### Step 2 - Find the install page

In `llms.txt`, find the Conversion Tracking overview and read it first. It compares the pixel and the API. Then find the page for the install path from Step 1, and the page that lists the event types and their parameters.

If the user is installing **both**, read the de-duplication page before writing any code. Both sources must send the same event ID for the same real-world action, so decide where the ID is generated before you write code.

### Step 3 - Install

For the **pixel**, install the snippet first and confirm it loads in the browser's DevTools Network tab. `PageView` fires automatically on load; add the other events one at a time with `kad("track", "EventName", { ... })`.

For the **Conversion API**, work in this order — the identifiers are the part integrations get wrong:

1. Get the advertiser ID and generate an API key (the key is shown once; the user must store it).
2. Set up persistence for `user_id` and `kad_cid` before sending any events. `user_id` must be stable across every event from the same visitor; `kad_cid` arrives as a query parameter on the ad click and must survive later navigations. Server-set HTTP-only cookies are the recommended mechanism.
3. Only then send events to `POST https://app.koah.ai/api/v1/conversion_events`, with `Authorization: Bearer <API key>` and `Content-Type: application/json`.

API keys must be generated by the user — never guess or reuse one, and keep it server-side, never in client JavaScript.

### Step 4 - Verify

**Pixel**:

- Open the site in a browser, open the DevTools Network tab.
- Trigger the target event (purchase, signup, custom event).
- Confirm a request fires to `https://app.koah.ai/...` with the expected event payload.

**Conversion API**:

- Trigger the target event and inspect the API's JSON response.
- Confirm `messages` is empty. **A 200 does not mean the events were accepted** — per-event validation failures still return 200, each reported as `{ "index": N, "message": "..." }`. Accepted count is `events_received` minus the number of messages.
- Confirm the events carry `kad_cid` when the visitor arrived from a Koah ad; without it the conversion cannot be attributed to a campaign.

For both, the installation helper in the Koah dashboard confirms the events it has received.

### Conversion Tracking gotchas

- **Event ID naming differs by source**: the pixel takes `eventId` (camelCase, inside the parameters object); the Conversion API takes `event_id` (snake_case, on the event). They are the same value and must match when both sources report the same action. Truncated past 512 characters.
- **Event names are a fixed set**, not free-form — `PageView`, `Lead`, `SignUp`, `ViewContent`, `Search`, `Purchase`, `AddToCart`, `AddToWishlist`, `InitiateCheckout`. Anything else is rejected. Pick the closest supported name.
- **Conversion API — a 200 is not an acceptance**: per-event validation failures come back in a `messages` array with the failing event's `index`, still under HTTP 200. Always check `messages`, never just the status code.
- **Conversion API — `kad_cid` is optional but load-bearing**: events without it are accepted and stored, but cannot be attributed to a Koah campaign. Send it whenever the visitor arrived from a Koah ad. It must be a valid UUID.
- **Conversion API batching**: at most 100 events per request, and every event in one request must carry the same `advertiser_id`.

## References

- Content policy (what creatives are allowed): https://docs.koahlabs.com/content-policy
- Demo publisher IDs (for testing): https://docs.koahlabs.com/resources/troubleshooting/testing
- JavaScript FAQ: https://docs.koahlabs.com/sdk/javascript#faq