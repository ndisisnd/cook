<!-- Concern index for the security skill. cook matches task keywords/patterns against this table. -->
# security Skills Index

## Load Order

1. Always load `<SKILLS>/security/SKILL.md` — three P0 always-apply rules cover every code task.
2. Match the task's keywords and touched-file patterns against the Concern Match table below.
3. Load each listed file whose concern matches at least one signal.

## Concern Match

| Concern | File patterns | Keywords | Load |
| ------- | ------------- | -------- | ---- |
| **Credentials & secrets** | `**/.env*`, `**/config/**`, `**/secrets/**` | secret, api key, password, token, credential, hardcoded, dotenv | `core/hardcoded-credentials.md` |
| **Cryptography & key mgmt** | `**/crypto/**`, `**/keys/**`, `**/*.pem`, `**/*.crt`, `**/*.p12` | encrypt, decrypt, hash, hmac, aes, rsa, key, certificate, crypto, cipher | `core/crypto-algorithms.md`, `core/digital-certificates.md`, `core/additional-cryptography.md`, `owasp/cryptographic-storage.md`, `owasp/key-management.md` |
| **Authentication & MFA** | `**/auth/**`, `**/login/**`, `**/*.guard.*` | auth, login, password, mfa, 2fa, otp, sso, credential stuffing, forgot password, account recovery | `core/authentication-mfa.md`, `owasp/authentication.md`, `owasp/multifactor-authentication.md`, `owasp/password-storage.md`, `owasp/credential-stuffing-prevention.md`, `owasp/forgot-password.md` |
| **OAuth, JWT & SAML** | `**/auth/**`, `**/oauth/**`, `**/token/**` | oauth, oauth2, jwt, saml, openid, oidc, bearer, access token, refresh token | `owasp/oauth2.md`, `owasp/json-web-token-for-java.md`, `owasp/saml-security.md` |
| **Authorization & access control** | `**/auth/**`, `**/middleware.*`, `**/*.guard.*`, `**/policies/**` | rbac, abac, role, permission, privilege, idor, access control, mass assignment, least privilege, scope | `core/authorization-access-control.md`, `owasp/authorization.md`, `owasp/insecure-direct-object-reference-prevention.md`, `owasp/mass-assignment.md` |
| **Session management & cookies** | `**/session/**`, `**/middleware.*` | session, cookie, csrf, session fixation, session timeout, httponly, samesite, secure flag | `core/session-management-and-cookies.md`, `owasp/session-management.md`, `owasp/cross-site-request-forgery-prevention.md`, `owasp/cookie-theft-mitigation.md` |
| **Input validation & injection** | `**/controllers/**`, `**/routes/**`, `**/handlers/**` | sql injection, injection, input validation, parameterize, ldap, command injection, prototype pollution, sanitize | `core/input-validation-injection.md`, `owasp/input-validation.md`, `owasp/injection-prevention.md`, `owasp/sql-injection-prevention.md`, `owasp/os-command-injection-defense.md`, `owasp/ldap-injection-prevention.md`, `owasp/prototype-pollution-prevention.md` |
| **XSS & client-side security** | `**/*.html`, `**/*.tsx`, `**/*.jsx`, `**/components/**` | xss, cross-site scripting, dom xss, dangerouslysetinnerhtml, innerhtml, csp, clickjacking, ajax, xs-leaks | `core/client-side-web-security.md`, `owasp/xss-prevention.md`, `owasp/content-security-policy.md`, `owasp/clickjacking-defense.md`, `owasp/xs-leaks.md` |
| **API & web services** | `**/controllers/**`, `**/routes/**`, `**/api/**` | api, rest, graphql, soap, ssrf, openapi, endpoint, cors, rate limit | `core/api-web-services.md`, `owasp/rest-security.md`, `owasp/graphql.md`, `owasp/server-side-request-forgery-prevention.md` |
| **HTTP transport & headers** | `**/middleware.*`, `**/server.*` | tls, ssl, https, hsts, http header, strict-transport-security, pinning, transport security | `owasp/transport-layer-security.md`, `owasp/http-headers.md`, `owasp/pinning.md` |
| **Data storage & privacy** | `**/*.entity.ts`, `**/migrations/**`, `**/repositories/**` | database, storage, pii, privacy, gdpr, encryption at rest, rls, row-level security, data classification | `core/data-storage.md`, `core/privacy-data-protection.md`, `owasp/database-security.md`, `owasp/user-privacy-protection.md` |
| **File handling & uploads** | `**/upload/**`, `**/files/**`, `**/storage/**` | file upload, multipart, mime, attachment, blob | `core/file-handling-and-uploads.md`, `owasp/file-upload.md` |
| **XML & serialization** | `**/*.xml`, `**/*.xsd`, `**/*.xslt` | xml, xxe, serialization, deserialization, dtd, entity, pickle, yaml load | `core/xml-and-serialization.md`, `owasp/xml-external-entity-prevention.md`, `owasp/deserialization.md`, `owasp/xml-security.md` |
| **Logging & monitoring** | `**/logging/**`, `**/observability/**`, `**/telemetry/**` | logging, audit log, security event, monitoring, alerting, redact, pii in logs | `core/logging.md`, `owasp/error-handling.md` |
| **Redirects** | `**/routes/**`, `**/controllers/**` | redirect, open redirect, url redirect, forward, location header | `owasp/redirects.md` |
| **Supply chain & dependencies** | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `requirements.txt`, `Gemfile.lock` | dependency, supply chain, sbom, npm, third-party, provenance, integrity hash | `core/supply-chain-security.md`, `owasp/vulnerable-dependency-management.md`, `owasp/npm-security.md` |
| **DevOps, CI/CD & containers** | `.github/workflows/**`, `Dockerfile`, `docker-compose*.yml`, `Jenkinsfile`, `.gitlab-ci.yml` | docker, ci, cd, pipeline, artifact, container, image, devops | `core/devops-ci-cd-containers.md`, `owasp/ci-cd-security.md`, `owasp/docker-security.md` |
| **Kubernetes & cloud** | `**/k8s/**`, `**/helm/**`, `**/*.yaml` (k8s context) | kubernetes, k8s, helm, pod security, network policy, admission, secret rotation | `core/cloud-orchestration-kubernetes.md`, `owasp/kubernetes-security.md` |
| **Infrastructure as Code** | `**/*.tf`, `**/*.tfvars`, `**/cloudformation/**`, `**/pulumi/**` | terraform, cloudformation, pulumi, iac, bicep, ansible | `core/iac-security.md` |
| **Mobile security** | `**/*.swift`, `**/*.kt`, `**/android/**`, `**/ios/**` | ios, android, mobile, swift, kotlin, biometric, keychain, keystore | `core/mobile-apps.md`, `owasp/mobile-application-security.md` |
| **MCP & AI security** | `**/mcp/**`, `**/.mcp.json`, `**/tools/**` (MCP context) | mcp, model context protocol, llm, ai tool, agentic, tool use, prompt injection | `core/mcp-security.md` |
| **C/C++ memory safety** | `**/*.c`, `**/*.cpp`, `**/*.h`, `**/*.hpp` | buffer overflow, memory safety, strcpy, sprintf, gets, string safety | `core/safe-c-functions.md` |
| **Microservices & zero trust** | `**/services/**`, `**/mesh/**` | microservices, zero trust, service mesh, network segmentation, mtls | `owasp/microservices-security.md`, `owasp/zero-trust-architecture.md`, `owasp/network-segmentation.md` |
| **Framework: Node.js** | `server.{ts,js}`, `app.{ts,js}`, `**/server/**` | node.js, nodejs, express, fastify, nestjs, hono | `core/framework-and-languages.md`, `owasp/nodejs-security.md`, `owasp/npm-security.md` |
| **Framework: Python / Django** | `**/*.py`, `manage.py`, `settings.py` | django, drf, flask, python, fastapi | `core/framework-and-languages.md`, `owasp/django-security.md`, `owasp/django-rest-framework.md` |
| **Framework: Java** | `**/*.java`, `pom.xml`, `build.gradle` | java, spring, jakarta, jvm | `core/framework-and-languages.md`, `owasp/java-security.md`, `owasp/bean-validation.md` |
| **Framework: PHP** | `**/*.php`, `composer.json` | php, laravel, symfony | `core/framework-and-languages.md`, `owasp/php-configuration.md`, `owasp/laravel.md`, `owasp/symfony.md` |
| **Framework: Ruby** | `**/*.rb`, `Gemfile` | ruby, rails, sinatra | `core/framework-and-languages.md`, `owasp/ruby-on-rails.md` |
| **Framework: .NET** | `**/*.cs`, `**/*.csproj` | dotnet, .net, c#, asp.net, blazor | `core/framework-and-languages.md`, `owasp/dotnet-security.md` |

## Notes

- The three always-apply rules (`hardcoded-credentials`, `crypto-algorithms`, `digital-certificates`) are checked on every task — they are not in the concern table.
- Each concern row may list multiple files; load all that apply.
- `core/` files are language-agnostic and broadly applicable. `owasp/` files provide detailed, domain-specific checklists.
- When multiple concerns apply (e.g. authentication + OAuth + session), load files for all matching concerns.
