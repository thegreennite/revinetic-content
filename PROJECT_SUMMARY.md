# What I'm Building — Revinetic AI Content Engine

## The one-line version

An AI system that researches, writes, grades, and publishes social media content for Revinetic (my AI marketing/automation company) to Facebook and Instagram, 4 times a day, every day, running entirely in the cloud with no manual posting from me — built and wired together in a single overnight session with Claude, then handed off to a fully autonomous scheduled agent.

## Why

This is the first real experiment for The Business Algorithm Podcast (TBAP): instead of talking about AI automation, build a working piece of it, in public, and show what actually happens — including the failures. Revinetic is the implementation engine; TBAP is the documentation of it. This project is both at once — it's a real operational asset for Revinetic's own marketing, and it's raw material for TBAP content about what it actually takes to automate a business function end to end.

The content itself follows creators I study — Alex Finn (early, hands-on with new AI tools), Sabrina Ramonov (builder/operator receipts: "I did X, here's what happened"), Nate Herk (automation/workflow infrastructure) — filtered through Revinetic's own wedge: most people overthink AI adoption into paralysis. Start before it's perfect. Improve daily.

## What it actually does, every day

1. **Reads brand context** from a private repo (`revinetic-content`): voice, audience, the core wedge, exact brand colors pulled from revinetic.com's actual CSS, and its own operating instructions.
2. **Checks recent post history** to avoid repeating hooks or topics.
3. **Generates 4 fresh post topics**, rotating across the four creator-inspired angles above, preferring specific client-style stories (a real HVAC voice-agent result, a dead-leads-list recovery) over abstract commentary about itself.
4. **Writes each post**: hook + body + CTA, iterating the hook through multiple variations and a "first 3 words" scroll-stop test before writing the body.
5. **Grades every post itself** across 7 weighted dimensions (hook strength is 50% of the score) and will not publish anything scoring below 8.0/10 — it rewrites and re-grades until it clears the bar.
6. **Generates an on-brand image** for each post (1080x1080, black background, lime accent, the real brand colors) using Python/Pillow, and hosts it by pushing to a second, public GitHub repo (`revinetic-images`) and linking the raw file URL directly — no manual upload step, because GoHighLevel's API doesn't actually require images to live in its own storage, it just needs a public URL.
7. **Publishes through GoHighLevel's API** to Facebook and Instagram — always a dry-run first, then the real call, then a follow-up read to confirm the platform actually accepted it (the create call returning success only means GoHighLevel accepted the request, not that Meta published it — that distinction mattered in practice: a post can silently fail on an expired token even after a "success" response).
8. **Saves a record of everything posted** back to the repo so tomorrow's run has real history to avoid repeating itself.
9. **Runs on a fixed schedule** — starts at 6:00 AM, first post goes out at 7:00 AM, three more spaced through the day at 11 AM, 3 PM, and 7 PM — entirely inside Anthropic's cloud infrastructure. No dependency on my laptop, my wifi, or me being awake.

## What it's built on

- **GoHighLevel** — the CRM/marketing platform Revinetic already runs on, connected via its official MCP server, using a scoped private integration token
- **Two GitHub repos** — one private (brand strategy, post history), one public (image hosting only, since GoHighLevel just needs a fetchable URL and the CCR checkout can only write to a repo the GitHub App has write access to)
- **A scheduled cloud agent** (a "routine") — not a script on my machine, a standing autonomous session that spins up daily in Anthropic's own cloud, does the work, and reports back

## What actually broke, and what that's worth

Real failures so far, each one diagnosed and fixed rather than worked around:
- A Facebook/Instagram OAuth token expired mid-build and had to be reconnected — confirmed by the exact error message, not assumed.
- GoHighLevel has no API for uploading a raw image file — solved by realizing the post endpoint just needs any public URL, not GoHighLevel's own storage.
- The cloud agent's GitHub access is currently read-only, so it can draft and grade but can't always push new images or save history — a real, still-open permission issue on the GitHub App's side, not a design flaw.
- The very first "it's live" I reported turned out to be wrong — the API had accepted the post but Meta had actually rejected it. Every verification since has checked real platform status, not just API acceptance.

That last one is probably the most honest thing to say about the whole build: verify the outcome, not the acknowledgment. That applies to more than posting APIs.

## Status as of this writing

Multiple posts live and verified on both Facebook and Instagram, a working end-to-end pipeline proven manually, and a daily autonomous routine now configured for 8 posts/day (4 per platform) at fixed times — one remaining known blocker (GitHub write permissions) documented and flagged for a fix, everything else self-healing or already fixed in place.
