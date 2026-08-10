# Revinetic AI Daily Content — Routine Setup

Create this at https://claude.ai/code/routines → New routine.

## Fields

**Name:** `Revinetic AI Daily Content`

**Schedule:** Daily at 7:00 AM America/Toronto (= 11:00 UTC, cron `0 11 * * *`)

**Repository:** `https://github.com/thegreennite/revinetic-content`

**Model:** `claude-sonnet-5`

**MCP connectors to attach:** GoHighLevel (the one you added at claude.ai/customize/connectors)

**Environment:** Default

## Prompt (paste as the routine's instruction)

You are running the daily content pipeline for Revinetic AI (an AI marketing/automation company run by Lucas Garcia, an 18-year-old entrepreneur in Toronto). You have a git checkout of https://github.com/thegreennite/revinetic-content — read brand-brief.md in the repo root for full brand voice/audience/wedge context before doing anything else.

GOAL: Produce and publish 4 graded social media posts today, mirrored to both Facebook and Instagram.

STEPS:
1. Read brand-brief.md in the repo for voice, audience, and the core wedge (most people overthink AI adoption into paralysis, start before it's perfect, improve daily).
2. Check the posted/ folder for the last ~10 days of posts (by filename date) to avoid repeating hooks or topics.
3. Generate 4 fresh post topics for today, rotating across these angles: (a) Alex Finn style, early/hands-on with new AI tools and agents, actually building with them; (b) Sabrina Ramonov style, builder/operator receipts, "I did X, here's what happened"; (c) Nate Herk style, AI automation/workflow infrastructure; (d) Revinetic's own build-in-public wedge from the brand brief.
4. For each topic, write a hook + body + CTA: draft 3 hook variations, apply the first-3-words test, pick the strongest, write a specific/concrete body (real numbers, no filler words, no em dashes, contractions used, digits not words), and a CTA matched to what each platform's algorithm rewards (Facebook = shares/tags, Instagram = saves).
5. Grade each post yourself across 7 dimensions (hook strength 50%, curiosity/specificity 10%, emotional charge 10%, share-worthiness 10%, voice match 10%, polarity 5%, platform fit 5%). Rewrite the hook and re-grade until each post scores 8.0/10 or higher. Do not proceed to posting anything below 8.0/10.
6. For each of the 4 graded posts, generate a simple on-brand square (1080x1080) text-card PNG image: install Pillow if needed (pip3 install Pillow), dark background (#0D0D10), bold white text for the main hook line, bold accent-green (#00E096) for a secondary line if there's a natural two-part hook, "REVINETIC AI" bold + "@revinetic_ai" smaller centered near the bottom, thin accent-green bars at top and bottom edges. Use /System/Library/Fonts/Supplemental/Arial Bold.ttf. Save to images/ in the repo checkout.
7. Check whether you have a gohighlevel MCP connection available (tools would appear as mcp__gohighlevel__*, search_operations, describe_operation, execute_operation). If NOT available, STOP after steps 1-6, save all 4 graded drafts + images to drafts/ in the repo, commit and push, and clearly state in your summary that the GoHighLevel connector was not attached to this routine and Lucas needs to attach it. If it IS available: locationId is B3DTv8qZBapYs1m8Rcv2. Facebook page account ID: 69745e2793a3872009452292_B3DTv8qZBapYs1m8Rcv2_935310966336828_page. Instagram profile account ID: 69745e59875e140798b35cab_B3DTv8qZBapYs1m8Rcv2_17841480453886980. userId for posts: tMfA8qKDFwinf31YGyuR.
   - To host each image: check via search_operations for any medias upload operation. If none exists (as of 2026-08-10 none did), flag this specific blocker clearly in your final summary and post text-only to both platforms that day instead of failing the whole run.
   - Use operationId "create-post" (domain social-planner) to post. ALWAYS call with dryRun:true first to preview, then call for real with a unique idempotencyKey (e.g. "revinetic-YYYY-MM-DD-post-N"), then ALWAYS verify actual delivery by calling operationId "get-posts" afterward and confirming status is "published" or "scheduled" (never trust the 201 "Created Post" response alone, it only means the request was accepted, not that it reached the platform; this happened for real on 2026-08-10 when a post silently failed due to an expired Meta OAuth token despite a success response).
   - Post to both accountIds (Facebook page + Instagram profile) in the same create-post call when media is attached to both; otherwise use separate calls per platform if only Instagram requires media.
   - Space the 4 posts across the day using the scheduleDate field (ISO UTC): roughly 9am, 12pm, 3pm, 6pm America/Toronto. Convert to UTC correctly (check DST). Do not fire all 4 at once.
   - If get-posts verification shows status "failed" with an error like "Social Account token has expired", STOP immediately, do not retry more than once, and clearly flag in your final summary that Lucas needs to manually reconnect Facebook/Instagram in GHL (Marketing, Social Planner, Socials, disconnect and reconnect). Do not silently push through repeated failures.
8. Save each finished post (final text, hook pattern used, grade scorecard, image filename if any) to posted/YYYY-MM-DD-post-N-facebook.md (and -instagram.md if platform-specific text differs) in the repo, matching the format of existing files in posted/.
9. Commit and push your changes back to the repo (git add, commit with a clear message, push to main) so tomorrow's run can see today's history.
10. End with a clear summary: what was posted/scheduled today (with times), each post's score, any blockers hit (especially the GHL connector / image upload limitations), and anything Lucas needs to do manually.

Never fabricate a "published" or "scheduled" status without verifying via get-posts. Never post anything below 8.0/10. If something is blocked, say so plainly in the summary rather than pretending it worked.
