# Security Rules — Non-negotiable Security Policies

## Credential Management
- ❌ NEVER hardcode credentials in code
- ❌ NEVER commit .env files with real values
- ❌ NEVER log sensitive data (passwords, tokens, PII)
- ✅ Always use environment variables
- ✅ Always provide .env.example with dummy values
- ✅ Always add sensitive files to .gitignore

## Database Operations
- ❌ NEVER execute DELETE, DROP, TRUNCATE without explicit confirmation
- ❌ NEVER use raw string concatenation in queries
- ✅ Always use parameterized queries
- ✅ Always backup before destructive operations
- ✅ Prefer soft deletes over hard deletes

## API Security
- ✅ Validate all input data
- ✅ Sanitize output to prevent XSS
- ✅ Use HTTPS in production
- ✅ Implement rate limiting
- ✅ Use proper authentication (JWT, OAuth)
- ✅ Set CORS policies appropriately

## Git Security
- ❌ NEVER push to main/master directly
- ❌ NEVER force push to shared branches
- ✅ Use branch protection rules
- ✅ Require pull request reviews
- ✅ Scan for secrets before commit

## Container Security
- ✅ Use non-root users
- ✅ Use minimal base images
- ✅ Scan images for vulnerabilities
- ✅ Set resource limits
- ✅ Don't expose unnecessary ports

## Sensitive Data Patterns to Block
```
- API keys: /[A-Za-z0-9_-]{20,}/
- AWS keys: /AKIA[0-9A-Z]{16}/
- Private keys: /-----BEGIN.*PRIVATE KEY-----/
- Passwords in URLs: /://[^:]+:[^@]+@/
```
