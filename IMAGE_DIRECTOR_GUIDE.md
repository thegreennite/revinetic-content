# Image Director — Creative Direction Guide

This is a reasoning framework, not code — the Image Director step is judgment (what should this post look like, and why), so any Claude session running the daily pipeline follows this guide directly rather than calling a deterministic function. `pipeline/duplication_check.py` handles the deterministic half (comparing a proposed concept against real history).

## Process, per post

1. **Read the finished, graded caption.** Never generate an image before the post is written and graded — the image should serve the idea, not the other way around.
2. **Pick a TYPE** (A-F, see below) based on the post's category and what the caption actually needs.
3. **Build the structured concept** (see schema below) before writing the final image prompt.
4. **Check novelty**: run `pipeline/duplication_check.check_visual_duplication()` against `pipeline/post_history.json`. If it flags a repeat, change at least the subject, setting, or style before generating — don't ship the same visual recipe twice in a row.
5. **Write the final prompt** — concrete and specific, not "create an AI automation image." See the worked example below.
6. **Generate** via `pipeline/image_generator.generate_image()`.
7. **Record** the full concept + prompt + resulting URL into `post_history.json` so tomorrow's novelty check has real data.

## Concept schema (fill this in before prompting)

```json
{
  "core_idea": "",
  "visual_metaphor": "",
  "scene": "",
  "subject": "",
  "environment": "",
  "camera_angle": "",
  "composition": "",
  "lighting": "",
  "realism_level": "",
  "objects": "",
  "facial_expression": "",
  "branding": "",
  "text_in_image": false,
  "exact_text": null,
  "platform": "",
  "dimensions": "1080x1080",
  "emotional_response": "",
  "negative_constraints": ""
}
```

## Types (pick ONE, don't force the same type every time)

| Type | When to use |
|---|---|
| **A — Pure visual** | Default for client-story/receipts posts. Minimal-to-no text; the caption does the explaining. |
| **B — Visual + headline** | A strong one-line claim over a real/conceptual scene. Use when the hook alone is the whole idea. |
| **C — Editorial graphic** | Breaking AI news, model releases, stats. Tech-news/magazine styling. |
| **D — Diagram/workflow** | Explaining agents, CRM automation, MCP, APIs — anything with real structure to show. |
| **E — Meme/cultural** | Occasional, when genuinely funny. Don't overuse — this is not a meme account. |
| **F — Seasonal/event** | Only when a holiday/event has a real, non-forced angle to AI/business/automation. |

## Brand colors (from brand-brief.md — use exactly, never guess)
Black `#000000` background base · Lime `#9afe5a` primary accent · Muted green `#69A443` secondary · White `#FFFFFF` text. Branding should usually be **subtle** — a lime accent light, a green folder tab, a small UI sliver — not "everything on a black poster." Reserve heavy branding (Type B text-on-black) for when the post is specifically about Revinetic itself.

## Worked example (good vs bad prompt)

**Bad** (what NOT to write): `Create an AI automation image.`

**Good** (what to write instead):
> Photorealistic commercial advertising photograph of a small HVAC company's dispatch office at 11pm, dark room lit mainly by a computer monitor's soft glow and one small desk lamp, an office desk phone mid-ring in the foreground with a shallow depth of field, an empty ergonomic office chair behind it suggesting no one is physically there, realistic clutter of work order printouts and a coffee mug, a business folder with a subtle lime-green accent tab reflecting a small amount of green light, no people in frame, no visible screen text, no robots, no glowing digital brain, no holograms, no cyberpunk elements, premium editorial advertising photography style, cinematic, believable, square 1:1 composition.

The difference: real scene, real objects, real lighting logic, explicit negative constraints, one clear idea. Every prompt should be this specific.

## Standing negative constraints (default, unless the concept truly calls for one of these)
No robots. No glowing AI brains. No holograms. No generic cyberpunk cities. No malformed hands. No unreadable/garbled screen UI. No fake logos. No excessive text. No generic stock-photo smiles. No clutter overload.

## Quality bar
Minimum image score 8.0/10 (same bar as the post itself). If the generated image doesn't match the concept, looks like an obvious low-quality AI artifact, or duplicates a recent visual, regenerate with an adjusted prompt rather than shipping it.
