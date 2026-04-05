# Publishing Guide — How to Add New Pages

This guide covers the full workflow for creating and publishing a new entity page on Kite-knowledge — from generating the draft to seeing it live on the site.

---

## Overview: The 4-Step Publication Lifecycle

```
1. GENERATE  →  2. COMPLETE  →  3. PROMOTE  →  4. PUBLISH
  AI draft        Fill content     staging/        PR → CI →
  in staging/     & validate       → docs/         merge → live
```

All new content starts in `staging/` (private, not published) and moves to `docs/` (published) only after passing human validation and automated CI checks.

---

## Supported Entity Types

| Type | Directory | Example slug |
|------|-----------|-------------|
| `person` | `docs/people/` | `otto-lilienthal` |
| `brand` | `docs/brands/` | `prism-kite-technology` |
| `model` | `docs/models/` | `prism-synapse-delta` |
| `material` | `docs/materials/` | `ripstop-nylon` |
| `frame` | `docs/frames/` | `carbon-fiber-spreader` |
| `club` | `docs/clubs/` | `american-kitefliers-association` |
| `pilot` | `docs/pilots/` | `janet-wilson` |
| `timeline` | `docs/timeline/` | `1903-wright-brothers-flight` |

**Slug convention:** lowercase, hyphens only, no accents, no spaces. Must exactly match the `id:` field in frontmatter.

---

## Step 1 — Generate the Draft

Use the generator script to create a correctly structured draft file in `staging/`:

```bash
python scripts/generate_entity.py --type person --slug otto-lilienthal
```

This creates `staging/people/otto-lilienthal.md` with:
- All required frontmatter fields pre-filled as `TODO`
- `ai_status: draft` set automatically
- Correct file structure for the entity type

**Check the generated file:**

```bash
cat staging/people/otto-lilienthal.md
```

---

## Step 2 — Complete the Draft

Open the draft file and fill in every `TODO` field with accurate, sourced content.

### Required frontmatter fields (all entity types)

```yaml
---
id: "otto-lilienthal"          # Must match filename exactly
type: "person"                 # Entity type
title: "Otto Lilienthal"       # Display name
date_range: "1848-1896"        # Active period or lifespan
geography: "Germany"           # Primary geographic context
category: "pioneer"            # Classification within type
tags:
  - "person"
  - "glider"
  - "1890s"
related:
  - "../timeline/1891-lilienthal-glider.md"   # Use ../ for cross-directory links
summary: "One sentence describing the entity for the EntityHeader component."
ai_status: "draft"             # Do NOT change yet — see Step 2.4
source_verified: false         # Update to true only when sources are verified
reviewer: null                 # Fill in your GitHub username when ready
review_date: null              # Fill in today's date when ready
---
```

> **Important — `related:` path format:**  
> Always use `../` to navigate up from the entity's directory before the target type directory.  
> ✅ `"../timeline/1891-lilienthal-glider.md"` (from `docs/people/`)  
> ✅ `"../people/otto-lilienthal.md"` (from `docs/timeline/`)  
> ❌ `"timeline/1891-lilienthal-glider.md"` (missing `../`)

### Writing the page body

Structure your page body with these sections (adapt as needed for the entity type):

```markdown
# Otto Lilienthal

## Summary
[Expanded summary — 2-3 sentences]

## Key Facts
| Field | Value |
|---|---|
| Born | 23 May 1848, Anklam, Prussia |
| Died | 10 August 1896, Berlin |
| Known for | Glider flights |

## Historical Context
[2-4 paragraphs of historical context]

## Timeline Anchor
See [Event Title](../timeline/slug.md) for the event context.

## Sources
- Author, Title, Publisher, Year.
- URL or archive reference.
```

### Validate source quality

Before marking as validated, verify:
- [ ] Every factual claim has a corresponding source listed in `## Sources`
- [ ] At least one source is independently verifiable (book, archive, academic paper)
- [ ] Dates, names, and attributions are cross-checked

### Update frontmatter for promotion

Once content is complete and sources verified:

```yaml
ai_status: "validated"         # Required by promote_staging.py
source_verified: true          # Only set to true if ALL sources are verified
reviewer: "your-github-username"
review_date: "2026-04-05"      # Today's date
```

> `in-review` is an optional intermediate state for collaborative review (e.g., ask a colleague to check). The promotion script requires `validated` — not `in-review`.

---

## Step 3 — Validate and Promote

### Run local validation first

```bash
# Validate frontmatter against schema
python scripts/validate_frontmatter.py staging/people/otto-lilienthal.md
```

Fix any errors before promoting. Common errors and solutions:

| Error | Solution |
|-------|----------|
| `Missing required field: reviewer` | Add `reviewer: "your-username"` |
| `Missing required field: review_date` | Add `review_date: "YYYY-MM-DD"` |
| `id mismatch: frontmatter id='...' but filename slug='...'` | Ensure `id:` field matches filename exactly |
| `Invalid value for 'ai_status'` | Must be `draft`, `in-review`, or `validated` |

### Promote to `docs/`

```bash
python scripts/promote_staging.py staging/people/otto-lilienthal.md
```

The script will:
1. Verify `ai_status: validated`, `reviewer` is set, and `source_verified: true`
2. Move the file from `staging/people/` to `docs/people/`
3. Print instructions for the next step

If the script exits with an error, fix the reported issue and re-run.

---

## Step 4 — Open a Pull Request

### Commit and push your branch

```bash
git checkout -b add-person-otto-lilienthal
git add docs/people/otto-lilienthal.md
git commit -m "feat: add person otto-lilienthal"
git push origin add-person-otto-lilienthal
```

### Open the PR on GitHub

1. Go to `https://github.com/remynollet/Kite-knowledge`
2. GitHub will show a banner: **"Compare & pull request"** — click it
3. Set the base branch to `main`
4. Title format: `feat: add [type] [slug]` (e.g., `feat: add person otto-lilienthal`)
5. Click **Create pull request**

### CI gate — what runs automatically

| Check | What it verifies |
|-------|-----------------|
| Frontmatter validation | All required fields present and correctly typed in `docs/` |
| AI draft gate | No `ai_status: draft` in `docs/` (validated content only) |
| Link check | No broken internal links, including `related:` frontmatter |
| MkDocs strict build | Site builds without warnings or errors |

All 4 checks must pass (green) before the PR can be merged.

### If CI fails

Click on the failing check to see the error log. Common fixes:

- **Frontmatter validation fails:** Open the file in `docs/`, correct the reported field, commit and push.
- **Link check fails on `related:`:** Ensure the path uses `../` and the target file exists in `docs/`.
- **MkDocs build fails:** Ensure the new file is listed in `nav:` in `mkdocs.yml`.

---

## Step 5 — After Merge

Once the PR is merged to `main`:

1. The deploy workflow runs automatically (takes ~1–2 minutes)
2. The site is updated at `https://remynollet.github.io/Kite-knowledge/`
3. Your new page is live

---

## Adding the new page to site navigation

If the new page should appear in the site navigation, add it to `mkdocs.yml` under the appropriate section:

```yaml
nav:
  - People:
      - people/index.md
      - people/lawrence-hargrave.md
      - people/otto-lilienthal.md    # ← Add here
```

Then commit the `mkdocs.yml` change along with the new page in the same PR.

---

## Quick Reference — Full workflow

```bash
# 1. Generate draft
python scripts/generate_entity.py --type person --slug otto-lilienthal

# 2. Edit the file and fill in all TODO fields
# staging/people/otto-lilienthal.md

# 3. Validate locally
python scripts/validate_frontmatter.py staging/people/otto-lilienthal.md

# 4. Promote to docs/
python scripts/promote_staging.py staging/people/otto-lilienthal.md

# 5. Create branch and PR
git checkout -b add-person-otto-lilienthal
git add docs/people/otto-lilienthal.md mkdocs.yml
git commit -m "feat: add person otto-lilienthal"
git push origin add-person-otto-lilienthal
# → Open PR on GitHub → Wait for CI → Merge → Live
```
