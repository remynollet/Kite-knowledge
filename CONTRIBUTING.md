# Contributing to Kite-knowledge

## Content Lifecycle

Every entity page follows a strict 4-state lifecycle before it can appear on the public site:

| State | Location | Conditions to enter | Who sets it |
|-------|----------|---------------------|-------------|
| `draft` | `staging/{type}/` | File created via `generate_entity.py` | Auto (script) |
| `in-review` | `staging/{type}/` | All mandatory fields filled, ≥1 source added, `promote_staging.py --to-review` run | Contributor |
| `validated` | `docs/{type}/` | Maintainer has reviewed content + sources, `reviewer` set, `source_verified: true` | Maintainer |
| `rejected` | `staging/{type}/` | Maintainer closes the PR; file stays in `staging/` with `ai_status: draft` reset | Maintainer |

**Transition conditions:**

- `draft` → `in-review`: all mandatory schema fields present, `reviewer: null` still allowed, at least one source listed, `promote_staging.py --to-review` exits 0
- `in-review` → `validated`: maintainer sets `ai_status: validated`, `reviewer: <username>`, `review_date: YYYY-MM-DD`, `source_verified: true`, then merges the PR
- `in-review` → `rejected`: maintainer closes the PR with written reason; contributor resets `ai_status: draft` and revises
- `rejected` → `in-review`: contributor addresses feedback, reruns `promote_staging.py --to-review`, opens new PR

> **Hard rule:** CI blocks any merge that introduces `ai_status: draft` into `docs/`. No exception.

---

## AI Draft → Publication Workflow

All content follows a 4-step staging-to-publication process:

### Step 1: Generate a Draft

```bash
python scripts/generate_entity.py --type person --slug peter-lynn
```

This creates `staging/people/peter-lynn.md` with all required frontmatter fields pre-filled as `TODO` placeholders and `ai_status: draft`.

### Step 2: Edit and Complete the Draft

1. Open `staging/people/peter-lynn.md`
2. Fill in all `TODO` fields with accurate content
3. Add at least one verifiable source in the `## Sources` section
4. When complete, submit for review:

```bash
python scripts/promote_staging.py staging/people/peter-lynn.md --to-review
```

This script validates mandatory fields and updates `ai_status: "in-review"`.

> **Note:** The final promotion to `docs/` via `promote_staging.py` (without `--to-review`) requires `ai_status: "validated"`. This state is typically set by the maintainer after successful review.

### Step 3: Validate and Promote (Maintainer)

Once the review is successful, the maintainer or authorized contributor performs the final promotion:

```bash
# Set ai_status: validated, reviewer, and source_verified: true manually in the file
python scripts/promote_staging.py staging/people/peter-lynn.md
```

The script verifies that `ai_status: validated`, `reviewer` is set, and `source_verified: true`. If all checks pass, it moves the file to `docs/people/peter-lynn.md` and prints PR instructions.

### Step 4: Open a Pull Request

```bash
git add .
git commit -m "feat: add person peter-lynn"
git push origin your-branch-name
```

Then open a PR targeting `main`. The CI gate will run several checks automatically:

1. **Step 0 — Staging Structure Check** — ensures the `staging/` directory structure is intact.
2. **Step 1 — Frontmatter lint** — all required fields present and correctly typed.
3. **Step 2 — AI draft block** — no `ai_status: draft` in `docs/`.
4. **Step 3 — Broken link check** — no broken internal links.
5. **Step 4 — MkDocs build** — no warnings or errors.

Merge is only allowed when all checks pass.

---

## Internationalization (i18n)

Kite-knowledge supports 5 core languages: **French (default), English, German, Italian, and Spanish**.

### How it works

The site uses the `mkdocs-static-i18n` plugin.
- A file named `filename.md` is served as the **French** version.
- A file named `filename.en.md` is served as the **English** version.
- Other extensions: `.de.md` (German), `.it.md` (Italian), `.es.md` (Spanish).

### Contributing Translations

1. Locate the validated file in `docs/` (e.g., `docs/people/peter-lynn.md`).
2. Create a copy with the language extension (e.g., `docs/people/peter-lynn.en.md`).
3. Translate the content and update the frontmatter if necessary (note: technical metadata like `related`, `patent_url`, `image` must remain identical).
4. Mark the file with `ai_translated: true` if generated via AI, and `ai_status: validated` once reviewed by a native speaker.

### Linguistic Ambassadors

If you are a native speaker of English, German, Italian, or Spanish, you can become a **Linguistic Ambassador**. Your role is to:
- Review AI-generated drafts (`ai_translated: true`).
- Ensure technical terminology is accurate according to the [Technical Glossary](glossary/index.md).
- Validate the natural flow of the translation.
- Set `ai_status: validated` and add your username as `reviewer`.

---

## Local Development

```bash
pip install -r requirements.txt
mkdocs serve
```

Site available at: http://127.0.0.1:8000

## Validate Frontmatter Locally

```bash
python scripts/validate_frontmatter.py docs/
python scripts/validate_frontmatter.py staging/people/peter-lynn.md
```

## Check Internal Links Locally

```bash
python scripts/check_links.py docs/
```

## Troubleshooting

### Relative Links Error in `related:`
Ensure you use the correct relative path format. Cross-directory links MUST start with `../`.
Example: From `people/peter-lynn.md` to `models/cody-war-kite.md`, use `../models/cody-war-kite.md`.

### CI Failure: "Missing staging subdirectories"
Ensure that `staging/` contains all 11 required subfolders (brands, clubs, festivals, frames, materials, models, people, pilots, shops, teams, timeline). If one is missing, create it (even if empty, with a `.gitkeep` file).
