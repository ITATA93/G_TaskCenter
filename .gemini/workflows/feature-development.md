# Workflow: Feature Development

## Purpose
Structured approach for implementing new features.

## Phases

### Phase 1: Planning
```
1. Read existing architecture docs
2. Identify affected files/modules
3. Design approach
4. Create TODO items
5. Get user approval if major change
```

### Phase 2: Implementation
```
1. Create feature branch
   git checkout -b feature/{name}

2. Implement in small increments
3. Write tests alongside code
4. Update docs as you go
```

### Phase 3: Testing
```
1. Run unit tests
2. Run integration tests (if applicable)
3. Manual testing checklist
4. Fix any issues
```

### Phase 4: Review
```
1. Self-review with code-reviewer agent
2. Check for security issues
3. Verify documentation is complete
4. Update CHANGELOG.md
```

### Phase 5: Integration
```
1. Commit with descriptive message
2. Push branch
3. Create pull request (if remote configured)
4. Update TODO.md
```

## Parallel Sub-agent Usage
For large features, use parallel agents:
```bash
# Example: New API endpoint with tests and docs
parallel-agents.sh \
  "Implement /api/users endpoint|code-analyst" \
  "Write tests for users endpoint|test-writer" \
  "Document users endpoint|doc-writer"
```

## Checklist
- [ ] Architecture reviewed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Code reviewed
- [ ] No security issues
- [ ] Committed and pushed
