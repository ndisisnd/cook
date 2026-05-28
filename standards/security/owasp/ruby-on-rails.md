---
description: Security requirements for Ruby on Rails applications — injection, XSS, CSRF, sessions, redirects, and headers
alwaysApply: false
---

# Ruby on Rails Security

## NEVER
- Pass user input to `eval`, `system`, `exec`, `spawn`, `open("| ...")`, `Process.exec/spawn`, or any `IO` method accepting a shell command
- Concatenate user input into ActiveRecord query strings
- Use `raw`, `html_safe`, or `<%==` to render untrusted content
- Redirect to `params[:url]` without validation
- Commit sensitive files: `config/database.yml`, `secret_token.rb`, `db/seeds.rb`, `*.sqlite3`

## ALWAYS
- Use parameterized ActiveRecord queries (`where("col = ?", val)`)
- Rely on Rails' automatic HTML escaping; use `sanitize` only for allow-listed HTML
- Enable `protect_from_forgery` in `ApplicationController`
- Use `config.force_ssl = true` in production
- Use database-backed sessions (`active_record_store`) for sensitive applications
- Validate redirect targets against an allowlist or extract path only
- Set security headers explicitly; run Brakeman in CI

## Key Configurations

```ruby
# Force HTTPS
config.force_ssl = true                         # production.rb

# DB-backed sessions
Project::Application.config.session_store :active_record_store

# CSRF
class ApplicationController < ActionController::Base
  protect_from_forgery

# Security headers
ActionDispatch::Response.default_headers = {
  'X-Frame-Options' => 'SAMEORIGIN',
  'X-Content-Type-Options' => 'nosniff',
  'X-XSS-Protection' => '0'
}
```

## Safe Redirect Pattern

```ruby
begin
  if path = URI.parse(params[:url]).path
    redirect_to path
  end
rescue URI::InvalidURIError
  redirect_to '/'
end
```

## CORS (rack-cors)

```ruby
config.middleware.use Rack::Cors do
  allow do
    origins 'someserver.example.com'            # never '*' in production
    resource %r{/users/\d+.json},
      headers: ['Origin', 'Accept', 'Content-Type'],
      methods: [:post, :get]
  end
end
```

## Checklist
- [ ] No shell-execution methods called with user input
- [ ] All DB queries parameterized; no string concatenation in `where`
- [ ] `raw`/`html_safe` absent from views rendering user data
- [ ] `protect_from_forgery` enabled
- [ ] `force_ssl = true` in production
- [ ] Redirects validated against allowlist or path-only extraction
- [ ] Sensitive config files gitignored
- [ ] Brakeman runs in CI; `bcrypt stretches ≥ 10` in production
