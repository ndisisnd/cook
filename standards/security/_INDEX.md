<!-- Concern index for the security skill. cook matches task keywords/patterns against this table. -->
# security Skills Index

## Load Order

1. Always load `<SKILLS>/security/SKILL.md` — three P0 always-apply rules cover every code task.
2. Match the task's keywords and touched-file patterns against the Concern Match table below.
3. Load each listed file whose concern matches at least one signal.

## Concern Match

| Concern | File patterns | Keywords | Load |
| ------- | ------------- | -------- | ---- |
| **Credentials & secrets** | `**/.env*`, `**/config/**`, `**/secrets/**` | secret, api key, password, token, credential, hardcoded, dotenv | `core/codeguard-1-hardcoded-credentials.md` |
| **Cryptography & key mgmt** | `**/crypto/**`, `**/keys/**`, `**/*.pem`, `**/*.crt`, `**/*.p12` | encrypt, decrypt, hash, hmac, aes, rsa, key, certificate, crypto, cipher | `core/codeguard-1-crypto-algorithms.md`, `core/codeguard-1-digital-certificates.md`, `core/codeguard-0-additional-cryptography.md`, `owasp/codeguard-0-cryptographic-storage.md`, `owasp/codeguard-0-key-management.md` |
| **Authentication & MFA** | `**/auth/**`, `**/login/**`, `**/*.guard.*` | auth, login, password, mfa, 2fa, otp, sso, credential stuffing, forgot password, account recovery | `core/codeguard-0-authentication-mfa.md`, `owasp/codeguard-0-authentication.md`, `owasp/codeguard-0-multifactor-authentication.md`, `owasp/codeguard-0-password-storage.md`, `owasp/codeguard-0-credential-stuffing-prevention.md`, `owasp/codeguard-0-forgot-password.md` |
| **OAuth, JWT & SAML** | `**/auth/**`, `**/oauth/**`, `**/token/**` | oauth, oauth2, jwt, saml, openid, oidc, bearer, access token, refresh token | `owasp/codeguard-0-oauth2.md`, `owasp/codeguard-0-json-web-token-for-java.md`, `owasp/codeguard-0-saml-security.md` |
| **Authorization & access control** | `**/auth/**`, `**/middleware.*`, `**/*.guard.*`, `**/policies/**` | rbac, abac, role, permission, privilege, idor, access control, mass assignment, least privilege, scope | `core/codeguard-0-authorization-access-control.md`, `owasp/codeguard-0-authorization.md`, `owasp/codeguard-0-insecure-direct-object-reference-prevention.md`, `owasp/codeguard-0-mass-assignment.md` |
| **Session management & cookies** | `**/session/**`, `**/middleware.*` | session, cookie, csrf, session fixation, session timeout, httponly, samesite, secure flag | `core/codeguard-0-session-management-and-cookies.md`, `owasp/codeguard-0-session-management.md`, `owasp/codeguard-0-cross-site-request-forgery-prevention.md`, `owasp/codeguard-0-cookie-theft-mitigation.md` |
| **Input validation & injection** | `**/controllers/**`, `**/routes/**`, `**/handlers/**` | sql injection, injection, input validation, parameterize, ldap, command injection, prototype pollution, sanitize | `core/codeguard-0-input-validation-injection.md`, `owasp/codeguard-0-input-validation.md`, `owasp/codeguard-0-injection-prevention.md`, `owasp/codeguard-0-sql-injection-prevention.md`, `owasp/codeguard-0-query-parameterization.md`, `owasp/codeguard-0-os-command-injection-defense.md`, `owasp/codeguard-0-ldap-injection-prevention.md`, `owasp/codeguard-0-prototype-pollution-prevention.md` |
| **XSS & client-side security** | `**/*.html`, `**/*.tsx`, `**/*.jsx`, `**/components/**` | xss, cross-site scripting, dom xss, dangerouslysetinnerhtml, innerhtml, csp, clickjacking, ajax, xs-leaks | `core/codeguard-0-client-side-web-security.md`, `owasp/codeguard-0-cross-site-scripting-prevention.md`, `owasp/codeguard-0-dom-based-xss-prevention.md`, `owasp/codeguard-0-content-security-policy.md`, `owasp/codeguard-0-clickjacking-defense.md`, `owasp/codeguard-0-xss-filter-evasion.md`, `owasp/codeguard-0-xs-leaks.md` |
| **API & web services** | `**/controllers/**`, `**/routes/**`, `**/api/**` | api, rest, graphql, soap, ssrf, openapi, endpoint, cors, rate limit | `core/codeguard-0-api-web-services.md`, `owasp/codeguard-0-rest-security.md`, `owasp/codeguard-0-graphql.md`, `owasp/codeguard-0-server-side-request-forgery-prevention.md` |
| **HTTP transport & headers** | `**/middleware.*`, `**/server.*` | tls, ssl, https, hsts, http header, strict-transport-security, pinning, transport security | `owasp/codeguard-0-transport-layer-security.md`, `owasp/codeguard-0-http-headers.md`, `owasp/codeguard-0-http-strict-transport-security.md`, `owasp/codeguard-0-pinning.md` |
| **Data storage & privacy** | `**/*.entity.ts`, `**/migrations/**`, `**/repositories/**` | database, storage, pii, privacy, gdpr, encryption at rest, rls, row-level security, data classification | `core/codeguard-0-data-storage.md`, `core/codeguard-0-privacy-data-protection.md`, `owasp/codeguard-0-database-security.md`, `owasp/codeguard-0-user-privacy-protection.md` |
| **File handling & uploads** | `**/upload/**`, `**/files/**`, `**/storage/**` | file upload, multipart, mime, attachment, blob | `core/codeguard-0-file-handling-and-uploads.md`, `owasp/codeguard-0-file-upload.md` |
| **XML & serialization** | `**/*.xml`, `**/*.xsd`, `**/*.xslt` | xml, xxe, serialization, deserialization, dtd, entity, pickle, yaml load | `core/codeguard-0-xml-and-serialization.md`, `owasp/codeguard-0-xml-external-entity-prevention.md`, `owasp/codeguard-0-deserialization.md`, `owasp/codeguard-0-xml-security.md` |
| **Logging & monitoring** | `**/logging/**`, `**/observability/**`, `**/telemetry/**` | logging, audit log, security event, monitoring, alerting, redact, pii in logs | `core/codeguard-0-logging.md`, `owasp/codeguard-0-error-handling.md`, `owasp/codeguard-0-logging-vocabulary.md` |
| **Redirects** | `**/routes/**`, `**/controllers/**` | redirect, open redirect, url redirect, forward, location header | `owasp/codeguard-0-open-redirect.md`, `owasp/codeguard-0-unvalidated-redirects-and-forwards.md` |
| **Supply chain & dependencies** | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `requirements.txt`, `Gemfile.lock` | dependency, supply chain, sbom, npm, third-party, provenance, integrity hash | `core/codeguard-0-supply-chain-security.md`, `owasp/codeguard-0-vulnerable-dependency-management.md`, `owasp/codeguard-0-npm-security.md` |
| **DevOps, CI/CD & containers** | `.github/workflows/**`, `Dockerfile`, `docker-compose*.yml`, `Jenkinsfile`, `.gitlab-ci.yml` | docker, ci, cd, pipeline, artifact, container, image, devops | `core/codeguard-0-devops-ci-cd-containers.md`, `owasp/codeguard-0-ci-cd-security.md`, `owasp/codeguard-0-docker-security.md` |
| **Kubernetes & cloud** | `**/k8s/**`, `**/helm/**`, `**/*.yaml` (k8s context) | kubernetes, k8s, helm, pod security, network policy, admission, secret rotation | `core/codeguard-0-cloud-orchestration-kubernetes.md`, `owasp/codeguard-0-kubernetes-security.md` |
| **Infrastructure as Code** | `**/*.tf`, `**/*.tfvars`, `**/cloudformation/**`, `**/pulumi/**` | terraform, cloudformation, pulumi, iac, bicep, ansible | `core/codeguard-0-iac-security.md` |
| **Mobile security** | `**/*.swift`, `**/*.kt`, `**/android/**`, `**/ios/**` | ios, android, mobile, swift, kotlin, biometric, keychain, keystore | `core/codeguard-0-mobile-apps.md`, `owasp/codeguard-0-mobile-application-security.md` |
| **MCP & AI security** | `**/mcp/**`, `**/.mcp.json`, `**/tools/**` (MCP context) | mcp, model context protocol, llm, ai tool, agentic, tool use, prompt injection | `core/codeguard-0-mcp-security.md` |
| **C/C++ memory safety** | `**/*.c`, `**/*.cpp`, `**/*.h`, `**/*.hpp` | buffer overflow, memory safety, strcpy, sprintf, gets, string safety | `core/codeguard-0-safe-c-functions.md`, `owasp/codeguard-0-safe-c-functions.md`, `owasp/codeguard-0-cw-memory-string-usage-guidelines.md`, `owasp/codeguard-0-c-based-toolchain-hardening.md` |
| **Microservices & zero trust** | `**/services/**`, `**/mesh/**` | microservices, zero trust, service mesh, network segmentation, mtls | `owasp/codeguard-0-microservices-security.md`, `owasp/codeguard-0-zero-trust-architecture.md`, `owasp/codeguard-0-network-segmentation.md` |
| **Framework: Node.js** | `server.{ts,js}`, `app.{ts,js}`, `**/server/**` | node.js, nodejs, express, fastify, nestjs, hono | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-nodejs-security.md`, `owasp/codeguard-0-npm-security.md` |
| **Framework: Python / Django** | `**/*.py`, `manage.py`, `settings.py` | django, drf, flask, python, fastapi | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-django-security.md`, `owasp/codeguard-0-django-rest-framework.md` |
| **Framework: Java** | `**/*.java`, `pom.xml`, `build.gradle` | java, spring, jakarta, jvm | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-java-security.md`, `owasp/codeguard-0-bean-validation.md` |
| **Framework: PHP** | `**/*.php`, `composer.json` | php, laravel, symfony | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-php-configuration.md`, `owasp/codeguard-0-laravel.md`, `owasp/codeguard-0-symfony.md` |
| **Framework: Ruby** | `**/*.rb`, `Gemfile` | ruby, rails, sinatra | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-ruby-on-rails.md` |
| **Framework: .NET** | `**/*.cs`, `**/*.csproj` | dotnet, .net, c#, asp.net, blazor | `core/codeguard-0-framework-and-languages.md`, `owasp/codeguard-0-dotnet-security.md` |

## Notes

- The three always-apply rules (`codeguard-1-*`) are checked on every task — they are not in the concern table.
- Each concern row may list multiple files; load all that apply.
- `core/` files are language-agnostic and broadly applicable. `owasp/` files provide detailed, domain-specific checklists.
- When multiple concerns apply (e.g. authentication + OAuth + session), load files for all matching concerns.
