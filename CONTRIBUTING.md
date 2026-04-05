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
4. When complete, manually update:
   - `ai_status: "validated"`
   - `reviewer: "your-github-username"`
   - `source_verified: true` (only if you have verified all sources)
   - `review_date: "YYYY-MM-DD"`

   > **Note:** `in-review` is an optional intermediate state for collaborative review. The promotion script (`promote_staging.py`) requires `ai_status: "validated"` — set this only once you are satisfied with the content and sources.

### Step 3: Validate and Promote

Run the validation + promotion script:

```bash
python scripts/promote_staging.py staging/people/peter-lynn.md
```

The script verifies that `ai_status: validated`, `reviewer` is set, and `source_verified: true`. If all checks pass, it moves the file to `docs/people/peter-lynn.md` and prints PR instructions.

### Step 4: Open a Pull Request

```bash
git add .
git commit -m "feat: add person peter-lynn"
git push origin your-branch-name
```

Then open a PR targeting `main`. The CI gate will run 4 checks automatically:

1. **Frontmatter lint** — all required fields present and correctly typed
2. **AI draft block** — no `ai_status: draft` in `docs/`
3. **Broken link check** — no broken internal links
4. **MkDocs strict build** — no warnings or errors

Merge is only allowed when all 4 checks pass.

---

## Repository Setup (Maintainer)

### Branch Protection (One-time Setup)

In GitHub repository **Settings → Branches → Add rule**:

- Branch name pattern: `main`
- ☑ Require a pull request before merging
- ☑ Require status checks to pass before merging
  - Add required check: `Content Validation`
- ☑ Require branches to be up to date before merging
- ☑ Do not allow bypassing the above settings

### GitHub Pages (One-time Setup)

After the first push to `main` triggers the deploy workflow (creating a `gh-pages` branch):

In GitHub repository **Settings → Pages**:

- Source: Deploy from branch `gh-pages` / `/ (root)`

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
