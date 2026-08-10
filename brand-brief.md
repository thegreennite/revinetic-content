# Brand Brief — Revinetic (TBAP voice)

> Captured: 2026-08-09, rewritten after Lucas's full master context.
> Update as the business evolves.

## Business
Revinetic — Lucas Garcia's AI-powered marketing and automation company. Started around GoHighLevel/Zapier/Twilio/Mailgun-style agency work (funnels, CRM, follow-up, chat/SMS automation), moving toward AI-powered growth infrastructure that runs a lead's full lifecycle (capture → qualify → personalize → follow up → book → notify → analyze) like an AI-powered employee, not a bundle of disconnected tools.

## Customer
Business owners who've been sold "AI tools" and "automation" as buzzwords and want to see it actually running inside a real business — not a demo, a working system. Same audience Alex Finn / Sabrina Ramonov / Nate Herk built followings on: curious about AI, tired of hype, want proof over promises.

## Primary CTA
Follow / DM to see how the system works — Revinetic content is lead gen for the agency itself, so the throughline CTA is usually "want this in your business? DM me" or a save/follow to keep watching the build. Confirm with Lucas if a specific offer should anchor this instead.

## Strong Opinion / Wedge
"Where hype meets reality." Lucas's stated rule: don't talk about AI/business tactics, test them and show what actually happened. The wedge for every post: most content in this space is advice with no receipts. Revinetic/TBAP content always has a real result attached — built it, ran it, here's what happened — even when the result is a failure.

## Story Vault
- Revinetic + TBAP are actively building a live AI content system (this one) — research → draft → grade (8/10+ bar) → post to Facebook/Instagram via GoHighLevel, with images and short-form video added over the following days.
- TBAP's whole premise: document Lucas going from an 18-year-old testing AI/business tactics to running increasingly sophisticated companies. Every build, including this one, is legitimate content.

## Voice
Builder/operator energy (Sabrina Ramonov), early-and-hands-on with new AI tools (Alex Finn), automation-and-infrastructure fluency (Nate Herk) — filtered through Lucas's own directness. Say "I used X to build Y, here's what happened," never "here are 10 AI tools." Young, sharp, impatient with fluff — not corporate-agency voice.

## Universal Voice Rules (apply to every post)
- Contractions always ("don't" not "do not")
- Active voice, short sentences
- Address the reader as "you"
- Numbers as digits ("3 tips" not "three tips")
- No em dashes — use commas, periods, or "..."
- One concrete idea per post, not three
- Specific details over generic statements — real numbers, real outcomes, real timeframes

## Visual Brand Colors (base colors pulled from revinetic.com's CSS, 2026-08-10; background swapped to black per Lucas's preference — use these exactly, do not guess new ones)
- Black (primary background): `#000000` — Lucas's explicit choice over the site's navy, keep this
- Lime accent (primary highlight/headline color): `#9afe5a`
- Muted green (secondary accent): `#69A443`
- White (body text): `#FFFFFF`
- Card template: black background, lime accent bars top/bottom, lime for the main hook line, white for the supporting line, "REVINETIC AI" in white + "@revinetic_ai" in muted green near the bottom.

## Image Hosting for Instagram Posts (fully automated, no manual upload — read this before posting any image)
GHL's create-post API does NOT require images to be uploaded to GHL's own Media Storage. The `media.url` field on a post just needs to be any public HTTPS URL — GHL/Meta fetch it directly. There is no file-upload operation exposed through the gohighlevel MCP tools (checked 2026-08-10, none exists), so never try to upload binary files through GHL and never ask Lucas to manually drag a file into GHL Media Storage — that's a dead workflow now.

**Correct process, fully self-serve:**
1. Generate the card image locally (or in the cloud checkout) as usual.
2. Save it into a git checkout of the PUBLIC repo `https://github.com/thegreennite/revinetic-images` (separate from this private `revinetic-content` repo — images only, no brand strategy text goes in the public repo).
3. Commit and push it to `main`.
4. Use `https://raw.githubusercontent.com/thegreennite/revinetic-images/main/<filename>.png` directly as the `media.url` in the create-post call. No GHL upload step, no human step.
5. Verified working 2026-08-10: pushed a PNG, confirmed `curl` returns HTTP 200 with correct content-type, then posted successfully to Instagram using that URL (published, real permalink returned).

Use a unique filename per post (e.g. date + short slug) so old images aren't overwritten before their post's history is worth keeping.
