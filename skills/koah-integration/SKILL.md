---
name: koah-integration
description: Install Koah's Ad SDK (publishers monetizing AI apps with native ads) or the Koah pixel for Conversion Tracking (advertisers measuring event ROI). Triggers on "Koah", "koahlabs", "koah.ai", "monetize an AI app", "native ads", "ad placement", "sponsored content", "track conversions", "install a pixel".
---

# Koah Integration

This skill helps install Koah, an ad network for AI applications. Koah ships two products:

1. **Ad SDK** - publishers monetize their app with native ads, embedded via iOS, Android, Flutter, React Native, React, or JavaScript.
2. **Conversion Tracking** - advertisers track ROI by installing the Koah pixel on a marketing site or via a tag manager.

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
- "How do I use Koah?"

## Procedure

### Step 1 - Confirm the product

If the user's intent is ambiguous, ask:

> "Are you monetizing an app with ads (Ad SDK), or installing the pixel to track conversions and events (Conversion Tracking)?"

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

If you have strong evidence for one, skip the question and proceed.

### Step 2 - Confirm the integration target

**For Ad SDK**, identify the framework. Prefer evidence from the project over asking:

- `Podfile` or `Package.swift` -> **iOS** (Swift)
- `build.gradle` or `settings.gradle.kts` -> **Android** (Kotlin)
- `pubspec.yaml` -> **Flutter** (Dart)
- `app.json` + `react-native` in `package.json` -> **React Native** (TypeScript)
- `react` in `package.json` (no React Native) -> **React** (web)
- HTML files with raw `<script>` tags, no framework -> **JavaScript** (vanilla)

If still unclear, ask: *"Which framework is your app - iOS (Swift), Android (Kotlin), Flutter, React Native, React (web), or vanilla JavaScript?"*

**For Conversion Tracking**, identify the install path:

- Site managed via Webflow -> **Webflow**
- Site built in Framer -> **Framer**
- Google Tag Manager container present in HTML -> **Google Tag Manager**
- Otherwise -> **Manual pixel** (raw JS snippet)

If unclear, ask: *"How do you want to install the pixel - manually (raw JS snippet), via Google Tag Manager, Webflow, or Framer?"*

### Step 3 - Fetch the right overview page

Once product + target are pinned down, fetch the matching overview page and follow its install steps verbatim.

**Ad SDK overview pages** (read these first - they cover framework-specific gotchas):

- iOS: https://docs.koahlabs.com/sdk/ios
- Android: https://docs.koahlabs.com/sdk/android
- Flutter: https://docs.koahlabs.com/sdk/flutter
- React Native: https://docs.koahlabs.com/sdk/react-native
- React: https://docs.koahlabs.com/sdk/react
- JavaScript: https://docs.koahlabs.com/sdk/javascript

**Conversion Tracking install pages**:

- Manual pixel: https://docs.koahlabs.com/conversion-tracking/koah-pixel
- Google Tag Manager: https://docs.koahlabs.com/conversion-tracking/google-tag-manager
- Webflow: https://docs.koahlabs.com/conversion-tracking/webflow
- Framer: https://docs.koahlabs.com/conversion-tracking/framer

For deeper references (theming, experiment tags, API reference, etc.), consult the doc sitemap at https://docs.koahlabs.com/llms.txt.

### Step 4 - Install minimally, then customize

Each SDK overview page has a minimal example. Start by getting that example running with a test publisher ID - verify the SDK loads and shows an ad - before layering in the developer's queries, conversation IDs, theming, or analytics tags.

For Conversion Tracking, install the pixel snippet first and confirm it loads in the browser's DevTools Network tab. Then wire specific event calls (e.g. `koah('event', '...')`) one at a time.

**Ask the user** for their publisher ID (Ad SDK) or advertiser ID (Conversion Tracking) if you don't see one in the codebase. Direct links to where the user can copy it from the Koah dashboard:

- Publisher ID: https://app.koah.ai/publisher/settings?tab=integration
- Advertiser ID: https://app.koah.ai/advertiser/settings?tab=brand

Do **not** leave placeholders like `YOUR_ADVERTISER_ID` or `YOUR_PUBLISHER_ID` in the code you write unless the user explicitly asks you to - these placeholders **will not** work.

### Step 5 - Verify before declaring done

Do not claim the integration is complete until the verification steps have been performed.

**Ad SDK**:

- A `KoahCard` (or platform equivalent) renders without errors.
- At least one ad displays in the test environment.
- Debug logs (e.g. iOS `KoahLogger`, Android Debug Inspector) show successful `/k/init` and `/query` requests.

**Conversion Tracking**:

- Open the site in a browser, open the DevTools Network tab.
- Trigger the target event (purchase, signup, custom event).
- Confirm a request fires to `https://app.koah.ai/...` with the expected event payload.

## Common gotchas

- **Demo keys**: never ship a demo publisher ID to production. Replace with a real one before launch.
- **iOS / SPM vs CocoaPods**: Koah ships as a Swift Package - don't try to install via CocoaPods. If the project uses CocoaPods for everything else, add Koah as an SPM dependency separately.
- **React Native / Expo**: Koah works with both bare RN and Expo (managed workflow), but the install steps differ. Confirm which one before following the page.
- **Conversion tracking dedup**: the pixel deduplicates events on `event_id` within a 24h window. Generate a unique `event_id` per real event.
- **Never invent** SDK APIs, component names, event names, configuration options, or installation commands. If a symbol, method, prop, or configuration key is not documented in Koah documentation, do not assume it exists. Always verify implementation details against the relevant documentation page before providing code.

## References

- Full doc sitemap: https://docs.koahlabs.com/llms.txt
- Marketing site: https://www.koahlabs.com
- Content policy (what creatives are allowed): https://docs.koahlabs.com/content-policy
- Demo publisher IDs (for testing): https://docs.koahlabs.com/demo-keys
- FAQ: https://docs.koahlabs.com/faq
