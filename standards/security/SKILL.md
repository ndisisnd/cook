---
name: security
description: Software security standards. Use when writing, reviewing, or modifying any code to enforce secure-by-default practices and prevent common vulnerabilities (OWASP Top 10, injection, auth, crypto, supply chain, etc.).
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

# Software Security Skill

Comprehensive security guidance for AI coding agents to generate secure code and prevent common vulnerabilities.

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
| No hardcoded secrets | `core/hardcoded-credentials.md` | Passwords, API keys, tokens, and credentials must never appear in source code |
| Approved crypto only | `core/crypto-algorithms.md` | Only modern, unbroken algorithms (no MD5, RC4, DES, static RSA, etc.) |
| Certificate hygiene | `core/digital-certificates.md` | Certificate validation, pinning, and lifecycle management |

### Step 2 — Concern-Specific Rules

Load the files for each security domain that applies to the task:

<!-- LANGUAGE_MAPPINGS_START -->
| Concern | Signals (keywords / file patterns) | Load |
| ------- | ---------------------------------- | ---- |
| **Credentials & secrets** | `secret`, `api key`, `password`, `.env`, `config`, hardcoded value | `core/hardcoded-credentials.md` *(always-apply)* |
| **Cryptography & key management** | `encrypt`, `decrypt`, `hash`, `hmac`, `aes`, `rsa`, `key`, `pem`, `certificate`, `crypto` | `core/crypto-algorithms.md`, `core/digital-certificates.md`, `core/additional-cryptography.md`, `owasp/cryptographic-storage.md`, `owasp/key-management.md`, `owasp/cw-cryptographic-security-guidelines.md` |
| **Authentication & MFA** | `auth`, `login`, `password`, `mfa`, `2fa`, `otp`, `sso`, `oauth`, `oidc`, `saml`, `credential stuffing`, `forgot password`, `account recovery` | `core/authentication-mfa.md`, `owasp/authentication.md`, `owasp/multifactor-authentication.md`, `owasp/password-storage.md`, `owasp/credential-stuffing-prevention.md`, `owasp/forgot-password.md`, `owasp/choosing-and-using-security-questions.md` |
| **OAuth, JWT & SAML** | `oauth`, `oauth2`, `jwt`, `json web token`, `saml`, `openid`, `oidc`, `bearer`, `access token`, `refresh token` | `owasp/oauth2.md`, `owasp/json-web-token-for-java.md`, `owasp/saml-security.md`, `owasp/jaas.md` |
| **Authorization & access control** | `rbac`, `abac`, `rebac`, `role`, `permission`, `privilege`, `idor`, `access control`, `mass assignment`, `least privilege`, `scope` | `core/authorization-access-control.md`, `owasp/authorization.md`, `owasp/insecure-direct-object-reference-prevention.md`, `owasp/mass-assignment.md`, `owasp/transaction-authorization.md`, `owasp/authorization-testing-automation.md` |
| **Session management & cookies** | `session`, `cookie`, `session fixation`, `session timeout`, `csrf`, `csrf token`, `httponly`, `samesite`, `secure flag` | `core/session-management-and-cookies.md`, `owasp/session-management.md`, `owasp/cross-site-request-forgery-prevention.md`, `owasp/cookie-theft-mitigation.md` |
| **Input validation & injection** | `sql injection`, `injection`, `input validation`, `parameterize`, `ldap`, `command injection`, `prototype pollution`, `soql`, `nosql injection`, `sanitize` | `core/input-validation-injection.md`, `owasp/input-validation.md`, `owasp/injection-prevention.md`, `owasp/sql-injection-prevention.md`, `owasp/os-command-injection-defense.md`, `owasp/ldap-injection-prevention.md`, `owasp/prototype-pollution-prevention.md` |
| **XSS & client-side security** | `xss`, `cross-site scripting`, `dom xss`, `dangerouslysetinnerhtml`, `innerhtml`, `csp`, `content security policy`, `clickjacking`, `x-frame-options`, `ajax`, `third-party script`, `xs-leaks` | `core/client-side-web-security.md`, `owasp/xss-prevention.md`, `owasp/dom-clobbering-prevention.md`, `owasp/content-security-policy.md`, `owasp/clickjacking-defense.md`, `owasp/xs-leaks.md`, `owasp/ajax-security.md`, `owasp/html5-security.md`, `owasp/securing-cascading-style-sheets.md`, `owasp/third-party-javascript-management.md` |
| **API & web services** | `api`, `rest`, `graphql`, `soap`, `ssrf`, `server-side request forgery`, `openapi`, `web service`, `endpoint`, `cors`, `rate limit` | `core/api-web-services.md`, `owasp/rest-security.md`, `owasp/rest-assessment.md`, `owasp/graphql.md`, `owasp/server-side-request-forgery-prevention.md`, `owasp/web-service-security.md` |
| **HTTP transport & headers** | `tls`, `ssl`, `https`, `hsts`, `http header`, `strict-transport-security`, `certificate pinning`, `transport security` | `owasp/transport-layer-security.md`, `owasp/http-headers.md`, `owasp/pinning.md` |
| **Data storage & privacy** | `database`, `storage`, `pii`, `privacy`, `gdpr`, `data protection`, `encryption at rest`, `rls`, `row-level security`, `classification`, `data minimization` | `core/data-storage.md`, `core/privacy-data-protection.md`, `owasp/database-security.md`, `owasp/user-privacy-protection.md`, `owasp/cryptographic-storage.md` |
| **File handling & uploads** | `file upload`, `multipart`, `mime`, `attachment`, `file storage`, `blob`, `s3 upload` | `core/file-handling-and-uploads.md`, `owasp/file-upload.md` |
| **XML & serialization** | `xml`, `xxe`, `serialization`, `deserialization`, `dtd`, `entity`, `yaml load`, `pickle`, `json deserialization` | `core/xml-and-serialization.md`, `owasp/xml-external-entity-prevention.md`, `owasp/deserialization.md`, `owasp/xml-security.md` |
| **Logging & monitoring** | `logging`, `log`, `audit log`, `security event`, `monitoring`, `alerting`, `siem`, `redact`, `pii in logs` | `core/logging.md`, `owasp/error-handling.md` |
| **Redirects** | `redirect`, `open redirect`, `url redirect`, `forward`, `location header` | `owasp/redirects.md` |
| **Supply chain & dependencies** | `dependency`, `supply chain`, `sbom`, `npm`, `package lock`, `third-party`, `provenance`, `integrity hash` | `core/supply-chain-security.md`, `owasp/vulnerable-dependency-management.md`, `owasp/npm-security.md` |
| **DevOps, CI/CD & containers** | `docker`, `dockerfile`, `ci`, `cd`, `pipeline`, `github actions`, `artifact`, `container`, `image`, `registry`, `devops`, `virtual patching` | `core/devops-ci-cd-containers.md`, `owasp/ci-cd-security.md`, `owasp/docker-security.md`, `owasp/nodejs-docker.md` |
| **Kubernetes & cloud orchestration** | `kubernetes`, `k8s`, `helm`, `rbac`, `network policy`, `pod security`, `admission`, `secret rotation` | `core/cloud-orchestration-kubernetes.md`, `owasp/kubernetes-security.md` |
| **Infrastructure as Code** | `terraform`, `cloudformation`, `pulumi`, `iac`, `bicep`, `ansible`, `infrastructure as code` | `core/iac-security.md` |
| **Microservices & zero trust** | `microservices`, `zero trust`, `service mesh`, `network segmentation`, `mtls`, `sidecar` | `owasp/microservices-security.md`, `owasp/zero-trust-architecture.md`, `owasp/network-segmentation.md` |
| **Mobile security** | `ios`, `android`, `mobile`, `swift`, `kotlin`, `flutter`, `biometric`, `keychain`, `keystore`, `certificate pinning` | `core/mobile-apps.md`, `owasp/mobile-application-security.md` |
| **MCP & AI security** | `mcp`, `model context protocol`, `llm`, `ai tool`, `agentic`, `tool use`, `prompt injection` | `core/mcp-security.md` |
| **C/C++ memory safety** | `c`, `c++`, `buffer overflow`, `memory safety`, `strcpy`, `sprintf`, `gets`, `string safety`, `toolchain hardening` | `core/safe-c-functions.md` |
| **Framework: Node.js** | `node.js`, `nodejs`, `express`, `fastify`, `nestjs`, `hono` | `core/framework-and-languages.md`, `owasp/nodejs-security.md`, `owasp/nodejs-docker.md`, `owasp/npm-security.md` |
| **Framework: Python / Django** | `django`, `drf`, `flask`, `python`, `fastapi` | `core/framework-and-languages.md`, `owasp/django-security.md`, `owasp/django-rest-framework.md` |
| **Framework: Java** | `java`, `spring`, `jakarta`, `jvm`, `maven`, `gradle` | `core/framework-and-languages.md`, `owasp/java-security.md`, `owasp/jaas.md`, `owasp/bean-validation.md` |
| **Framework: PHP** | `php`, `laravel`, `symfony` | `core/framework-and-languages.md`, `owasp/php-configuration.md`, `owasp/laravel.md`, `owasp/symfony.md` |
| **Framework: Ruby** | `ruby`, `rails`, `sinatra` | `core/framework-and-languages.md`, `owasp/ruby-on-rails.md` |
| **Framework: .NET** | `dotnet`, `.net`, `c#`, `asp.net`, `blazor` | `core/framework-and-languages.md`, `owasp/dotnet-security.md` |
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
- Will this handle credentials? → Load `core/hardcoded-credentials.md`
- What language / framework? → Identify applicable framework rules from the table
- What security domains are involved? → Load relevant concern files from the table

### While writing code
- Apply secure-by-default patterns from the loaded rules
- Use parameterized queries, encode output, enforce access checks

### After writing code
- Verify no hardcoded credentials or secrets
- Check that applicable rules are satisfied
- Explain which security rules were applied and why
