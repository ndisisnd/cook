---
description: Node.js Docker security — hardened image construction for production deployments
alwaysApply: false
---

# Node.js Docker Security

## NEVER
- Use `FROM node` or `FROM node:latest` (non-deterministic)
- Run the container as root — always switch to the `node` user
- Use `CMD "npm" "start"` — npm doesn't forward OS signals
- Use bare `CMD ["node", "server.js"]` with Node as PID 1 — signals not handled
- Copy secrets (`.npmrc`, credentials) into final image layers
- Omit a `.dockerignore` file

## ALWAYS
- Pin base image with tag AND SHA256 digest: `FROM node:lts-alpine@sha256:<hash>`
- Install production deps only: `RUN npm ci --omit=dev`
- Set `ENV NODE_ENV production`
- Run as `node` user; `COPY --chown=node:node` all app files
- Use an init process (`dumb-init`) as PID 1
- Use multi-stage builds to separate build from production image
- Mount secrets via BuildKit — never `COPY` them
- Regularly scan images for vulnerabilities

## Dockerfile pattern

```dockerfile
FROM node:lts-alpine@sha256:<hash>
RUN apk add dumb-init
ENV NODE_ENV production
USER node
WORKDIR /usr/src/app
COPY --chown=node:node --from=build /usr/src/app/node_modules ./node_modules
COPY --chown=node:node . .
CMD ["dumb-init", "node", "server.js"]
```

## Graceful shutdown

```javascript
async function closeGracefully(signal) {
  await server.close()
  process.exit()
}
process.on('SIGINT', closeGracefully)
process.on('SIGTERM', closeGracefully)
```

## .dockerignore (required)
`node_modules`, `npm-debug.log`, `Dockerfile`, `.git`, `.gitignore`, `.npmrc`

## Checklist
- [ ] Base image pinned with tag and SHA256
- [ ] `npm ci --omit=dev` used; no dev deps in production image
- [ ] `NODE_ENV=production` set
- [ ] Container runs as `node` user, not root
- [ ] `dumb-init` (or equivalent) is PID 1
- [ ] Multi-stage build separates build and runtime
- [ ] Secrets mounted via BuildKit, not copied into layers
