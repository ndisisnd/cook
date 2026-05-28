---
name: security
description: Software security standards based on Project CodeGuard. Use when writing, reviewing, or modifying any code to enforce secure-by-default practices and prevent common vulnerabilities (OWASP Top 10, injection, auth, crypto, supply chain, etc.).
codeguard-version: "0.1.0"
framework: "Project CodeGuard"
purpose: "Embed secure-by-default practices into AI coding workflows"
metadata:
  triggers:
    files:
      - '**/auth/**'
      - '**/middleware.*'
      - '**/crypto/**'
      - '**/security/**'
      - '**/login/**'
      - '**/*.guard.*'
      - '**/upload/**'
      - 'Dockerfile'
      - 'docker-compose*.yml'
      - '.github/workflows/**'
      - '**/k8s/**'
      - '**/terraform/**'
    keywords:
      - security
      - auth
      - login
      - password
      - secret
      - credential
      - token
      - jwt
      - oauth
      - csrf
      - xss
      - sql injection
      - injection
      - encrypt
      - crypto
      - hash
      - certificate
      - tls
      - https
      - sanitize
      - validate
      - owasp
      - vulnerability
      - exploit
      - permission
      - rbac
      - authorization
      - privilege
      - pii
      - gdpr
---

# Software Security Skill (Project CodeGuard)

Comprehensive security guidance for AI coding agents to generate secure code and prevent common vulnerabilities. Based on **Project CodeGuard**, an open-source, model-agnostic framework that embeds secure-by-default practices into AI coding workflows.

## When to Use This Skill

Activate when:
- Writing new code in any language
- Reviewing or modifying existing code
- Implementing security-sensitive features (authentication, cryptography, data handling, etc.)
- Working with user input, databases, APIs, or external services
- Configuring cloud infrastructure, CI/CD pipelines, or containers
- Handling sensitive data, credentials, or cryptographic operations

## How to Use This Skill

### Step 1 — Always-Apply Rules

Check these on **every** code operation, regardless of language or context:

| Rule | File | What it governs |
| ---- | ---- | --------------- |
| No hardcoded secrets | `core/codeguard-1-hardcoded-credentials.md` | Passwords, API keys, tokens, and credentials must never appear in source code |
| Approved crypto only | `core/codeguard-1-crypto-algorithms.md` | Only modern, unbroken algorithms (no MD5, RC4, DES, static RSA, etc.) |
| Certificate hygiene | `core/codeguard-1-digital-certificates.md` | Certificate validation, pinning, and lifecycle management |

### Step 2 — Concern-Specific Rules

Load the files for each security domain that applies to the task:

<!-- LANGUAGE_MAPPINGS_START -->
| Concern | Signals (keywords / file patterns) | Load |
| ------- | ---------------------------------- | ---- |
| **Credentials & secrets** | `secret`, `api key`, `password`, `.env`, `config`, hardcoded value | `core/codeguard-1-hardcoded-credentials.md` *(always-apply)* |
| **Cryptography & key management** | `encrypt`, `decrypt`, `hash`, `hmac`, `aes`, `rsa`, `key`, `pem`, `certificate`, `crypto` | `core/codeguard-1-crypto-algorithms.md`, `core/codeguard-1-digital-certificates.md`, `core/codeguard-0-additional-cryptography.md`, `owasp/codeguard-0-cryptographic-storage.md`, `owasp/codeguard-0-key-management.md`, `owasp/codeguard-0-cw-cryptographic-security-guidelines.md` |
| **Authentication & MFA** | `auth`, `login`, `password`, `mfa`, `2fa`, `otp`, `sso`, `oauth`, `oidc`, `saml`, `credential stuffing`, `forgot password`, `account recovery` | `core/codeguard-0-authentication-mfa.md`, `owasp/codeguard-0-authentication.md`, `owasp/codeguard-0-multifactor-authentication.md`, `owasp/codeguard-0-password-storage.md`, `owasp/codeguard-0-credential-stuffing-prevention.md`, `owasp/codeguard-0-forgot-password.md`, `owasp/codeguard-0-choosing-and-using-security-questions.md` |
| **OAuth, JWT & SAML** | `oauth`, `oauth2`, `jwt`, `json web token`, `saml`, `openid`, `oidc`, `bearer`, `access token`, `refresh token` | `owasp/codeguard-0-oauth2.md`, `owasp/codeguard-0-json-web-token-for-java.md`, `owasp/codeguard-0-saml-security.md`, `owasp/codeguard-0-jaas.md` |
| **Authorization & access control** | `rbac`, `abac`, `rebac`, `role`, `permission`, `privilege`, `idor`, `access control`, `mass assignment`, `least privilege`, `scope` | `core/codeguard-0-authorization-access-control.md`, `owasp/codeguard-0-authorization.md`, `owasp/codeguard-0-insecure-direct-object-reference-prevention.md`, `owasp/codeguard-0-mass-assignment.md`, `owasp/codeguard-0-transaction-authorization.md`, `owasp/codeguard-0-authorization-testing-automation.md` |
| **Session management & cookies** | `session`, `cookie`, `session fixation`, `session timeout`, `csrf`, `csrf token`, `httponly`, `samesite`, `secure flag` | `core/codeguard-0-session-management-and-cookies.md`, `owasp/codeguard-0-session-management.md`, `owasp/codeguard-0-cross-site-request-forgery-prevention.md`, `owasp/codeguard-0-cookie-theft-mitigation.md` |
| **Input validation & injection** | `sql injection`, `injection`, `input validation`, `parameterize`, `ldap`, `command injection`, `prototype pollution`, `soql`, `nosql injection`, `sanitize` | `core/codeguard-0-input-validation-injection.md`, `owasp/codeguard-0-input-validation.md`, `owasp/codeguard-0-injection-prevention.md`, `owasp/codeguard-0-sql-injection-prevention.md`, `owasp/codeguard-0-query-parameterization.md`, `owasp/codeguard-0-os-command-injection-defense.md`, `owasp/codeguard-0-ldap-injection-prevention.md`, `owasp/codeguard-0-prototype-pollution-prevention.md` |
| **XSS & client-side security** | `xss`, `cross-site scripting`, `dom xss`, `dangerouslysetinnerhtml`, `innerhtml`, `csp`, `content security policy`, `clickjacking`, `x-frame-options`, `ajax`, `third-party script`, `xs-leaks` | `core/codeguard-0-client-side-web-security.md`, `owasp/codeguard-0-cross-site-scripting-prevention.md`, `owasp/codeguard-0-dom-based-xss-prevention.md`, `owasp/codeguard-0-dom-clobbering-prevention.md`, `owasp/codeguard-0-content-security-policy.md`, `owasp/codeguard-0-clickjacking-defense.md`, `owasp/codeguard-0-xss-filter-evasion.md`, `owasp/codeguard-0-xs-leaks.md`, `owasp/codeguard-0-ajax-security.md`, `owasp/codeguard-0-html5-security.md`, `owasp/codeguard-0-securing-cascading-style-sheets.md`, `owasp/codeguard-0-third-party-javascript-management.md` |
| **API & web services** | `api`, `rest`, `graphql`, `soap`, `ssrf`, `server-side request forgery`, `openapi`, `web service`, `endpoint`, `cors`, `rate limit` | `core/codeguard-0-api-web-services.md`, `owasp/codeguard-0-rest-security.md`, `owasp/codeguard-0-rest-assessment.md`, `owasp/codeguard-0-graphql.md`, `owasp/codeguard-0-server-side-request-forgery-prevention.md`, `owasp/codeguard-0-web-service-security.md` |
| **HTTP transport & headers** | `tls`, `ssl`, `https`, `hsts`, `http header`, `strict-transport-security`, `certificate pinning`, `transport security` | `owasp/codeguard-0-transport-layer-security.md`, `owasp/codeguard-0-http-headers.md`, `owasp/codeguard-0-http-strict-transport-security.md`, `owasp/codeguard-0-pinning.md` |
| **Data storage & privacy** | `database`, `storage`, `pii`, `privacy`, `gdpr`, `data protection`, `encryption at rest`, `rls`, `row-level security`, `classification`, `data minimization` | `core/codeguard-0-data-storage.md`, `core/codeguard-0-privacy-data-protection.md`, `owasp/codeguard-0-database-security.md`, `owasp/codeguard-0-user-privacy-protection.md`, `owasp/codeguard-0-cryptographic-storage.md` |
| **File handling & uploads** | `file upload`, `multipart`, `mime`, `attachment`, `file storage`, `blob`, `s3 upload` | `core/codeguard-0-file-handling-and-uploads.md`, `owasp/codeguard-0-file-upload.md` |
| **XML & serialization** | `xml`, `xxe`, `serialization`, `deserialization`, `dtd`, `entity`, `yaml load`, `pickle`, `json deserialization` | `core/codeguard-0-xml-and-serialization.md`, `owasp/codeguard-0-xml-external-entity-prevention.md`, `owasp/codeguard-0-deserialization.md`, `owasp/codeguard-0-xml-security.md` |
| **Logging & monitoring** | `logging`, `log`, `audit log`, `security event`, `monitoring`, `alerting`, `siem`, `redact`, `pii in logs` | `core/codeguard-0-logging.md`, `owasp/codeguard-0-error-handling.md`, `owasp/codeguard-0-logging-vocabulary.md` |
| **Redirects** | `redirect`, `open redirect`, `url redirect`, `forward`, `location header` | `owasp/codeguard-0-open-redirect.md`, `owasp/codeguard-0-unvalidated-redirects-and-forwards.md` |
| **Supply chain & dependencies** | `dependency`, `supply chain`, `sbom`, `npm`, `package lock`, `third-party`, `provenance`, `integrity hash` | `core/codeguard-0-supply-chain-security.md`, `owasp/codeguard-0-vulnerable-dependency-management.md`, `owasp/codeguard-0-npm-security.md` |
| **DevOps, CI/CD & containers** | `docker`, `dockerfile`, `ci`, `cd`, `pipeline`, `github actions`, `artifact`, `container`, `image`, `registry`, `devops`, `virtual patching` | `core/codeguard-0-devops-ci-cd-containers.md`, `owasp/codeguard-0-ci-cd-security.md`, `owasp/codeguard-0-docker-security.md`, `owasp/codeguard-0-nodejs-docker.md` |
| **Kubernetes & cloud orchestration** | `kubernetes`, `k8s`, `helm`, `rbac`, `network policy`, `pod security`, `admission`, `secret rotation` | `core/codeguard-0-cloud-orchestration-kubernetes.md`, `owasp/codeguard-0-kubernetes-security.md` |
| **Infrastructure as Code** | `terraform`, `cloudformation`, `pulumi`, `iac`, `bicep`, `ansible`, `infrastructure as code` | `core/codeguard-0-iac-security.md` |
| **Microservices & zero trust** | `microservices`, `zero trust`, `service mesh`, `network segmentation`, `mtls`, `sidecar` | `owasp/codeguard-0-microservices-security.md`, `owasp/codeguard-0-zero-trust-architecture.md`, `owasp/codeguard-0-network-segmentation.md` |
| **Mobile security** | `ios`, `android`, `mobile`, `swift`, `kotlin`, `flutter`, `biometric`, `keychain`, `keystore`, `certificate pinning` | `core/codeguard-0-mobile-apps.md`, `owasp/codeguard-0-mobile-application-security.md` |
| **MCP & AI security** | `mcp`, `model context protocol`, `llm`, `ai tool`, `agentic`, `tool use`, `prompt injection` | `core/codeguard-0-mcp-security.md` |
| **C/C++ memory safety** | `c`, `c++`, `buffer overflow`, `memory safety`, `strcpy`, `sprintf`, `gets`, `string safety`, `toolchain hardening` | `core/codeguard-0-safe-c-functions.md`, `owasp/codeguard-0-safe-c-functions.md`, `owasp/codeguard-0-cw-memory-string-usage-guidelines.md`, `owasp/codeguard-0-c-based-toolchain-hardening.md` |
| **Framework: Node.js** | `node.js`, `nodejs`, `express`, `fastify`, `nestjs`, `hono` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-nodejs-security.md`, `owasp/codeguard-0-nodejs-docker.md`, `owasp/codeguard-0-npm-security.md` |
| **Framework: Python / Django** | `django`, `drf`, `flask`, `python`, `fastapi` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-django-security.md`, `owasp/codeguard-0-django-rest-framework.md` |
| **Framework: Java** | `java`, `spring`, `jakarta`, `jvm`, `maven`, `gradle` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-java-security.md`, `owasp/codeguard-0-jaas.md`, `owasp/codeguard-0-bean-validation.md` |
| **Framework: PHP** | `php`, `laravel`, `symfony` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-php-configuration.md`, `owasp/codeguard-0-laravel.md`, `owasp/codeguard-0-symfony.md` |
| **Framework: Ruby** | `ruby`, `rails`, `sinatra` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-ruby-on-rails.md` |
| **Framework: .NET** | `dotnet`, `.net`, `c#`, `asp.net`, `blazor` | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-dotnet-security.md` |
<!-- LANGUAGE_MAPPINGS_END -->

### Step 3 — Proactive Security

Beyond avoiding vulnerabilities, actively implement secure patterns:
- Parameterized queries for all database access — never string-concatenated SQL
- Validate and sanitize all untrusted input at every system boundary
- Apply least-privilege principles to all services, roles, and data access
- Use only approved cryptographic algorithms from Step 1
- Implement defense-in-depth: multiple independent controls, not a single gate

## Workflow

### Before writing code
- Will this handle credentials? → Load `core/codeguard-1-hardcoded-credentials.md`
- What language / framework? → Identify applicable framework rules from the table
- What security domains are involved? → Load relevant concern files from the table

### While writing code
- Apply secure-by-default patterns from the loaded rules
- Use parameterized queries, encode output, enforce access checks

### After writing code
- Verify no hardcoded credentials or secrets
- Check that applicable rules are satisfied
- Explain which security rules were applied and why
