## Review Checklist

Before approving and merging this PR, the maintainer must verify all items below.

### Structure Compliance
- [ ] Entity file is placed in `docs/{type}/{slug}.md` — correct section for entity type
- [ ] Filename slug matches the `id:` field in frontmatter (no mismatch)
- [ ] Page structure includes: `# Title`, `## Summary`, `## Key Facts`, `## Sources` sections

### Frontmatter Completeness
- [ ] All mandatory fields are present and non-null: `id`, `type`, `title`, `date_range`, `geography`, `category`, `tags`, `related`, `summary`, `ai_status`, `source_verified`
- [ ] `ai_status:` is `validated` (not `draft` or `in-review`)
- [ ] `reviewer:` is set to a valid GitHub username (not null)
- [ ] `review_date:` is set to today's date in `YYYY-MM-DD` format
- [ ] `source_verified: true` (not false or null)

### Source Visibility
- [ ] At least one source is listed under `## Sources`
- [ ] Each source is specific enough to be independently verifiable (no "Wikipedia" or "general knowledge")
- [ ] All external URLs are live and resolve correctly

### Taxonomy Consistency
- [ ] `tags:` list includes at least one tag matching the entity `type:` value
  (e.g., a `person` entity must have `"person"` in tags)
- [ ] `category:` value is appropriate for the entity type (see schema docs)

### Content Quality
- [ ] Summary is one clear, factual sentence — no fluff or excessive hedging
- [ ] Key facts table values are accurate and match the narrative
- [ ] `related:` links point to files that actually exist in `docs/`

### CI Gate
- [ ] All 4 CI steps pass (Frontmatter Lint, Draft Block, Link Check, MkDocs Build)

---

**Reviewer notes:**
<!-- Add any notes, concerns, or feedback for the contributor here -->
