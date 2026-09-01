---
name: koah
description: Install Koah's Ad SDK (publishers monetizing AI apps with native ads) or Koah Conversion Tracking — the browser pixel, the server-side Conversion API, or both (advertisers measuring event ROI). Triggers on "Koah", "koahlabs", "koah.ai", "monetize an AI app", "native ads", "ad placement", "sponsored content", "track conversions", "install a pixel", "conversion API", "CAPI", "server-side conversion tracking".
---

# Koah Integration

This skill helps install Koah, an ad network for AI applications. Koah ships two products:

1. **Ad SDK** - publishers monetize their app with native ads, embedded via iOS, Android, Flutter, React Native, React, or JavaScript.
2. **Conversion Tracking** - advertisers track ROI by reporting visitor actions to Koah. Two reporting methods, usable separately or together: the **pixel** (a JavaScript snippet that reports from the visitor's browser) and the **Conversion API** (a REST endpoint your server posts to).

Before using any documentation URL, fetch and read the LLM-friendly docs sitemap:

https://docs.koahlabs.com/llms.txt

Use the sitemap to locate the latest canonical page for the user's framework. Prefer sitemap-discovered URLs over hardcoded URLs if they differ.

## When to use this skill

Use this skill when the user asks for help with anything Koah-related - installation, integration, troubleshooting, or "how do I" questions. Specific triggers:

- "Add Koah to my app"
- "Set up the Koah SDK"
- "Install Koah pixel"
- "Monetize my AI chatbot"
- "Track conversions on my landing page"
- "Set up the Koah conversion API" / "server-side conversion tracking"
- "How do I use Koah?"

## Procedure

### Step 1 - Confirm the product

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

If you have strong evidence for one, skip the question and proceed.

### Step 2 - Confirm the integration target

**For Ad SDK**, identify the framework. Prefer evidence from the project over asking:

- `Podfile` or `Package.swift` -> **iOS** (Swift)
- `build.gradle` or `settings.gradle.kts` -> **Android** (Kotlin)
- `pubspec.yaml` -> **Flutter** (Dart)
- `app.json` + `react-native` in `package.json` -> **React Native** (TypeScript)
- `react` in `package.json` (no React Native) -> **JavaScript** (the script-tag SDK works in React — gate `requestAd` on `window.koah` and pass a ref'd element as `target`)
- HTML files with raw `<script>` tags, no framework -> **JavaScript** (vanilla)

If still unclear, ask: *"Which framework is your app - iOS (Swift), Android (Kotlin), Flutter, React Native, React (web), or vanilla JavaScript?"*

**For Conversion Tracking**, resolve two things: the reporting method, then the install path.

First, the **reporting method**. If the user hasn't said, ask:

> "Do you want the browser pixel (quickest, but misses visitors with ad blockers or analytics disabled), the server-side Conversion API (more reliable, needs backend code), or both?"

Cues for **pixel**: no backend to change, a site builder (Webflow/Framer), a tag manager, or the user isn't a developer.
Cues for **Conversion API**: an existing server they control, a CSP or security policy against third-party scripts, or a stated concern about ad blockers and tracking reliability.
Cues for **both**: the user wants maximum coverage. Both is the most accurate option and the most work — it requires shared event IDs, see Step 3.

Then the **install path**:

- Pixel, site managed via Webflow -> **Webflow**
- Pixel, site built in Framer -> **Framer**
- Pixel, Google Tag Manager container present in HTML -> **Google Tag Manager**
- Pixel, otherwise -> **Manual pixel** (raw JS snippet)
- Conversion API -> **Manual API installation** (backend code; the GTM path for the API is not shipped yet)

### Step 3 - Fetch the right overview page

Once product + target are pinned down, fetch the matching overview page and follow its install steps verbatim.

**Ad SDK overview pages** (read these first - they cover framework-specific gotchas):

- iOS: https://docs.koahlabs.com/sdk/ios
- Android: https://docs.koahlabs.com/sdk/android
- Flutter: https://docs.koahlabs.com/sdk/flutter
- React Native: https://docs.koahlabs.com/sdk/react-native
- React (web) / JavaScript: https://docs.koahlabs.com/sdk/javascript

**Upgrading an existing Koah 0.x integration?** 1.0 is a breaking release — follow the platform's migration guide instead of re-installing from scratch:

- iOS: https://docs.koahlabs.com/sdk/ios/migration
- Android: https://docs.koahlabs.com/sdk/android/migration
- Flutter: https://docs.koahlabs.com/sdk/flutter/migration
- React Native: https://docs.koahlabs.com/sdk/react-native/migration

**Conversion Tracking pages**:

Start with the overview, which compares the pixel and the API and their trade-offs:

- Overview: https://docs.koahlabs.com/conversion-tracking

Pixel install:

- Manual pixel: https://docs.koahlabs.com/conversion-tracking/koah-pixel
- Google Tag Manager: https://docs.koahlabs.com/conversion-tracking/google-tag-manager
- Webflow: https://docs.koahlabs.com/conversion-tracking/webflow
- Framer: https://docs.koahlabs.com/conversion-tracking/framer

Conversion API install:

- Manual API installation: https://docs.koahlabs.com/conversion-tracking/api/manual-installation

Shared by both:

- Event types and their parameters: https://docs.koahlabs.com/conversion-tracking/events
- Installing both — de-duplicating events: https://docs.koahlabs.com/conversion-tracking/combined/deduplicating-events

If the user is installing **both**, read the de-duplication page before writing any code. Both sources must send the same event ID for the same real-world action, and that constraint shapes where the ID is generated — it is far cheaper to design for than to retrofit.

For deeper references (theming, experiment tags, API reference, etc.), consult the doc sitemap at https://docs.koahlabs.com/llms.txt.

### Step 4 - Install minimally, then customize

Each SDK overview page has a minimal example. Start by getting that example running with a test publisher ID - verify the SDK loads and shows an ad - before layering in the developer's queries, conversation IDs, theming, or analytics tags.

For the **pixel**, install the snippet first and confirm it loads in the browser's DevTools Network tab. `PageView` fires automatically on load; add the other events one at a time with `kad("track", "EventName", { ... })`.

For the **Conversion API**, work in this order — the identifiers are the part integrations get wrong:

1. Get the advertiser ID and generate an API key (the key is shown once; the user must store it).
2. Set up persistence for `user_id` and `kad_cid` before sending any events. `user_id` must be stable across every event from the same visitor; `kad_cid` arrives as a query parameter on the ad click and must survive later navigations. Server-set HTTP-only cookies are the recommended mechanism.
3. Only then send events to `POST https://app.koah.ai/api/v1/conversion_events`, with `Authorization: Bearer <API key>` and `Content-Type: application/json`.

**Ask the user** for their publisher ID (Ad SDK) or advertiser ID (Conversion Tracking) if you don't see one in the codebase. API keys must be generated by the user — never guess or reuse one, and keep it server-side, never in client JavaScript. Direct links to the Koah dashboard:

- Publisher ID: https://app.koahlabs.com/publisher/settings?tab=integration
- Advertiser ID: https://app.koahlabs.com/advertiser/settings?tab=brand
- API keys (Conversion API): https://app.koahlabs.com/advertiser/settings?tab=api_keys

Do **not** leave placeholders like `YOUR_ADVERTISER_ID` or `YOUR_PUBLISHER_ID` in the code you write unless the user explicitly asks you to - these placeholders **will not** work.

### Step 5 - Verify before declaring done

Do not claim the integration is complete until the verification steps have been performed.

**Ad SDK**:

- A `KoahCard` (or platform equivalent) renders without errors.
- At least one ad displays in the test environment.
- Debug logs (enable `debug`/`logLevel` per the [debugging guide](https://docs.koahlabs.com/concepts/debugging)) show successful `/k/init` and ad requests.

**Conversion Tracking - pixel**:

- Open the site in a browser, open the DevTools Network tab.
- Trigger the target event (purchase, signup, custom event).
- Confirm a request fires to `https://app.koah.ai/...` with the expected event payload.

**Conversion Tracking - Conversion API**:

- Trigger the target event and inspect the API's JSON response.
- Confirm `messages` is empty. **A 200 does not mean the events were accepted** — per-event validation failures still return 200, each reported as `{ "index": N, "message": "..." }`. Accepted count is `events_received` minus the number of messages.
- Confirm the events carry `kad_cid` when the visitor arrived from a Koah ad; without it the conversion cannot be attributed to a campaign.

For both, the installation helper in the Koah dashboard confirms the events it has received.

## Common gotchas

- **Demo keys**: never ship a demo publisher ID to production. Replace with a real one before launch.
- **iOS / SPM vs CocoaPods**: Koah ships as a Swift Package - don't try to install via CocoaPods. If the project uses CocoaPods for everything else, add Koah as an SPM dependency separately.
- **React Native / Expo**: Koah works with both bare RN and Expo (managed workflow), but the install steps differ. Confirm which one before following the page.
- **Event ID naming differs by source**: the pixel takes `eventId` (camelCase, inside the parameters object); the Conversion API takes `event_id` (snake_case, on the event). They are the same value and must match when both sources report the same action. Truncated past 512 characters.
- **Event names are a fixed set**, not free-form — `PageView`, `Lead`, `SignUp`, `ViewContent`, `Search`, `Purchase`, `AddToCart`, `AddToWishlist`, `InitiateCheckout`. Anything else is rejected. Pick the closest supported name.
- **Conversion API — a 200 is not an acceptance**: per-event validation failures come back in a `messages` array with the failing event's `index`, still under HTTP 200. Always check `messages`, never just the status code.
- **Conversion API — `kad_cid` is optional but load-bearing**: events without it are accepted and stored, but cannot be attributed to a Koah campaign. Send it whenever the visitor arrived from a Koah ad. It must be a valid UUID.
- **Conversion API — never put the API key in client code.** It authenticates the advertiser account; it belongs on the server only.
- **Conversion API batching**: at most 100 events per request, and every event in one request must carry the same `advertiser_id`.
- **Never invent** SDK APIs, component names, event names, configuration options, or installation commands. If a symbol, method, prop, or configuration key is not documented in Koah documentation, do not assume it exists. Always verify implementation details against the relevant documentation page before providing code.

## References

- Full doc sitemap: https://docs.koahlabs.com/llms.txt
- Marketing site: https://www.koahlabs.com
- Content policy (what creatives are allowed): https://docs.koahlabs.com/content-policy
- Demo publisher IDs (for testing): https://docs.koahlabs.com/demo-keys
- FAQ: https://docs.koahlabs.com/faq
