# Sprint 1 Review Feedback

## Summary
- Sprint 1 delivers a solid backend foundation. Auth, DB schema/migrations, seed, middleware, and rate limiting are in place. Unit and integration tests cover critical paths. Docs and Docker support are provided. Overall, acceptance criteria for Sprint 1 are met.

## What’s Good
- Robust auth: JWT with 8h expiry, bcrypt, role-aware middleware, input validation (Joi), login rate limiting.
- Error handling: Central middleware maps validation/JWT/DB errors to consistent JSON responses.
- Database: Users and leave_requests tables with indexes and FKs; seed for HR admin; Knex migrations.
- Tests: Unit tests (JWT/password) and integration tests (auth flow, DB schema presence) present and meaningful.
- Dev experience: README is clear; .env.example provided; Docker Compose with Postgres for local dev.

## Gaps and Recommendations
- JWT secret enforcement: `src/utils/jwt.js` falls back to a default secret. In production, fail fast if `JWT_SECRET` is missing to avoid insecure defaults. Recommendation: throw when `NODE_ENV === 'production'` and secret is default/missing.
- DB connection exit behavior: `src/config/database.js` calls `process.exit(1)` on connection failure at import-time. This can abruptly terminate tests and tooling. Recommendation: only exit in production; in dev/test, log and rethrow so callers can handle gracefully.
- Test migrations setup: Integration tests expect tables to exist but don’t run migrations automatically. Recommendation: in `tests/setup.js` (or a global setup), run `knex migrate:latest` against the test DB, and rollback in teardown to keep tests self-contained.
- Rate-limit test coverage: Add a test that exceeds login attempts and asserts HTTP 429 with the configured message.
- HR seed login: Add an integration test that seeds (or inserts) the HR admin and verifies login, to explicitly satisfy “HR admin can login” acceptance.
- CORS configuration: Default `CORS_ORIGIN` is fine for dev; ensure production is restricted to known origins. Since tokens are sent via `Authorization` header, `credentials: true` isn’t required; consider disabling it unless you plan to use cookies.
- Error code consistency: Auth middleware returns `INVALID_TOKEN` for bad tokens while the error handler maps `JsonWebTokenError` to `AUTH_REQUIRED`. They’re consistent in practice because middleware handles it, but consider unifying codes for clarity and future maintainability.
- Docker dev vs prod mismatch: Dockerfile installs prod deps only (`npm ci --only=production`), but `docker-compose.yml` runs `npm run dev` (needs `nodemon`, a devDependency). This will fail inside the container. Recommendation: either install dev deps for the dev image (e.g., `npm ci`) or change compose to run `npm start` for the prod image. Alternately, use multi-stage Dockerfile (dev/prod).
- Secrets in logs: Seed script prints plaintext creds. That’s OK for local dev, but ensure this log isn’t enabled in staging/prod. Consider gating with `NODE_ENV`.
- Optional: Enforce stronger password policy (beyond min length) per PRD security posture and add tests (uppercase/lowercase/digit/special), if desired.

## Conclusion
- Sprint 1 meets its acceptance criteria. Please address the above items (especially JWT secret enforcement, test migrations setup, and Docker dev/prod alignment) early in Sprint 2 to reduce operational risk.

