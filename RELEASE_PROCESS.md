# Release Process

Monthly checklist for publishing a Kite-knowledge release journal entry.

## When to Publish

Release entries are published once per month, covering all content merged into `main` during that calendar month.

---

## Step-by-Step Checklist

### 1. Collect changes

Review `git log --oneline --since="YYYY-MM-01" --until="YYYY-MM-last-day"` and list all pages:

- Added to `docs/` (new entity pages)
- Modified in `docs/` (corrections, updates)
- Source references added or strengthened

### 2. Create the release file

```bash
# Create the entry file manually:
# docs/releases/YYYY-MM.md
```

Use the template below. All mandatory frontmatter fields must be filled.

**Frontmatter template:**

```yaml
---
id: "YYYY-MM"
type: "release"
title: "Month YYYY Release"
date_range: "YYYY-MM"
summary: "One-sentence summary of the release highlights."
tags:
  - "release"
related: []
ai_status: "validated"
source_verified: true
reviewer: "your-github-username"
review_date: "YYYY-MM-DD"
---
```

**Body template:**

```markdown
# Month YYYY Release

## Summary

One paragraph overview of what changed this month.

## Additions

- [Entity Title](../type/slug.md) — brief description of what was added

## Corrections

- [Entity Title](../type/slug.md) — brief description of what was corrected

## Source Strengthening

- [Entity Title](../type/slug.md) — brief description of which sources were added or verified
```

> Note: Omit a section entirely if there are no entries for it that month.

### 3. Update the release index

Add the new entry as the **first row** in the table in `docs/releases/index.md`:

```markdown
| [Month YYYY](YYYY-MM.md) | YYYY-MM-DD | One-line summary |
```

### 4. Validate locally

```bash
python scripts/validate_frontmatter.py docs/releases/YYYY-MM.md
python scripts/check_links.py docs/
mkdocs build --strict
```

All three must exit 0 before opening a PR.

### 5. Open a Pull Request

```bash
git add docs/releases/YYYY-MM.md docs/releases/index.md
git commit -m "release: publish YYYY-MM release journal entry"
git push origin release/YYYY-MM
```

Open a PR targeting `main`. The CI gate must pass all 4 checks before merging.

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| File | `YYYY-MM.md` | `2026-04.md` |
| Frontmatter `id` | `YYYY-MM` | `2026-04` |
| Frontmatter `title` | `Month YYYY Release` | `April 2026 Release` |
| PR branch | `release/YYYY-MM` | `release/2026-04` |
| Commit message | `release: publish YYYY-MM release journal entry` | `release: publish 2026-04 release journal entry` |

---

## Schema

Release entries are validated against `scripts/schemas/release.yaml`.
All mandatory fields must be non-null and correctly typed before CI will pass.
