---
description: Scheduled deep research to update project knowledge base
---
// turbo-all

# Deep Research Update Workflow

Run periodic research on configured topics to keep the knowledge base current.

## Steps

1. Read the research topics configuration:
   ```
   cat config/research_topics.yaml
   ```

2. For each topic in the config, check if `last_researched` is older than the schedule interval. If it is, execute a research query:
   ```
   Research the latest updates, features, breaking changes, and best practices for {topic.name}.
   Focus on: {topic.focus}
   Keywords: {topic.keywords}
   Only include changes since {topic.last_researched}.
   Output as structured markdown with: Executive Summary, New Features, Breaking Changes, Sources.
   ```

3. Save results to `docs/research/{DATE}_{topic_slug}.md` using the standard research output format

4. Update `config/research_topics.yaml` — set `last_researched` to today's date for each researched topic

5. Generate a summary of all findings:
   ```
   Write a brief executive summary of all research findings to docs/research/INDEX.md
   Include: topic, date researched, key findings (1-2 lines each)
   ```

6. Notify the user:
   ```
   "Research update complete. {N} topics researched. Key findings: [summary]"
   ```

## Manual Invocation

To research a single topic:
```
Research latest updates for {topic_name}. Save to docs/research/
```

To run full update:
```
Follow the /deep-research-update workflow
```

## Notes
- Research results persist in `docs/research/` and are indexed for future reference
- Each vendor uses its best research capability (Codex deep-research, Gemini, Claude web)
- Results are project-scoped — they stay in this project's repo
