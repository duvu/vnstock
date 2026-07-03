# Tasks: Phase 4 — Auth-aware Local Data Service

## 0. Prerequisite check

- [ ] Confirm Phase 1 platform contracts exist.
- [ ] Confirm Phase 2 provider plugins exist.
- [ ] Confirm Phase 3 health-aware routing exists or is planned as a prerequisite.
- [ ] Confirm TCBS legacy auth code is inventoried.
- [ ] Confirm service scope remains data-read only.

## 1. Auth core

- [ ] Create `vnstock/core/auth/`.
- [ ] Add auth type model.
- [ ] Add auth spec model.
- [ ] Add auth context model.
- [ ] Add auth policy model.
- [ ] Add session cache abstraction.
- [ ] Add safe diagnostics metadata model.
- [ ] Add redaction helper.
- [ ] Add tests for each auth model.

## 2. Credential store

- [ ] Add `CredentialStore` interface.
- [ ] Add memory credential store for tests.
- [ ] Add environment-backed credential store for controlled development use.
- [ ] Add restricted local file credential store.
- [ ] Add keyring credential store where supported.
- [ ] Add vault-compatible interface for future enterprise deployments.
- [ ] Add tests for read/write/delete behavior.
- [ ] Add tests for missing credential behavior.
- [ ] Add tests for safe diagnostics output.

## 3. Auth manager

- [ ] Add `AuthManager`.
- [ ] Implement provider auth context resolution.
- [ ] Implement provider login dispatch.
- [ ] Implement provider logout.
- [ ] Implement auth status.
- [ ] Implement credential availability checks.
- [ ] Ensure AuthManager does not expose raw credential material to callers.
- [ ] Add tests for login/status/logout flows using mocked providers.

## 4. Provider auth spec

- [ ] Add `auth_spec(dataset)` to provider plugin contract.
- [ ] Add no-auth spec for public providers.
- [ ] Add optional/experimental auth spec for TCBS.
- [ ] Mark TCBS authenticated mode as explicit-only.
- [ ] Ensure account, order, transfer, margin, and portfolio capabilities are out of scope.
- [ ] Add tests for provider auth spec declarations.

## 5. TCBS auth migration

- [ ] Wrap existing TCBS auth behind AuthManager.
- [ ] Preserve command-based manual login behavior.
- [ ] Remove provider-side direct auth state access where possible.
- [ ] Stop printing credential material when saving fails.
- [ ] Avoid exposing provider session details in user-facing errors.
- [ ] Store auth state through CredentialStore.
- [ ] Add tests for OTP-required flow with mocks.
- [ ] Add tests for failed login with safe error handling.
- [ ] Add tests that TCBS auth remains data-read only.

## 6. CLI auth commands

- [ ] Add `vnstock auth login PROVIDER`.
- [ ] Add `vnstock auth status`.
- [ ] Add `vnstock auth logout PROVIDER`.
- [ ] Add `vnstock auth delete PROVIDER`.
- [ ] Keep login interactive and local.
- [ ] Ensure CLI does not print sensitive credential material.
- [ ] Add CLI tests with mocked input/output.
- [ ] Keep legacy `vnstock-tcbs-login` as a compatibility shim or document deprecation.

## 7. Auth-aware routing

- [ ] Add auth policy handling to ProviderRouter.
- [ ] Support `forbid_authenticated`.
- [ ] Support `prefer_no_auth`.
- [ ] Support `allow_authenticated`.
- [ ] Support `require_authenticated`.
- [ ] Combine auth policy with provider health policy.
- [ ] Ensure authenticated providers are not selected by default unless policy allows.
- [ ] Add tests for each auth policy.

## 8. Local data service

- [ ] Create `vnstock/service/`.
- [ ] Add service app entrypoint.
- [ ] Add `vnstock serve` command.
- [ ] Add health endpoint.
- [ ] Add provider metadata endpoints.
- [ ] Add provider health endpoint.
- [ ] Add provider capabilities endpoint.
- [ ] Add safe auth status endpoint.
- [ ] Add data-read endpoints for market/reference/fundamental/fund datasets.
- [ ] Ensure service has no login endpoint.
- [ ] Ensure service has no account/order/portfolio endpoints.
- [ ] Add service tests.

## 9. Docker runtime

- [ ] Add Dockerfile.
- [ ] Add docker-compose example.
- [ ] Add local-only default binding.
- [ ] Add mounted auth/data volume.
- [ ] Add interactive login documentation for Docker.
- [ ] Add service healthcheck.
- [ ] Document single-user local scope.
- [ ] Document that public internet deployment is out of scope.

## 10. DataResult integration

- [ ] Attach safe auth metadata to `DataResult.diagnostics`.
- [ ] Attach safe auth metadata to `DataFrame.attrs` where appropriate.
- [ ] Preserve existing quality metadata.
- [ ] Add tests for safe auth diagnostics.
- [ ] Add tests for backward compatibility.

## 11. Endpoint allowlist and denylist

- [ ] Define allowed service endpoints.
- [ ] Define forbidden endpoint groups.
- [ ] Add tests that forbidden endpoints are absent.
- [ ] Add tests that service remains data-read only.

## 12. Documentation

- [ ] Add `docs/AUTH_AND_CREDENTIALS.md`.
- [ ] Add `docs/LOCAL_DATA_SERVICE.md`.
- [ ] Add `docs/DOCKER_RUNTIME.md`.
- [ ] Document CLI auth workflow.
- [ ] Document Docker auth workflow.
- [ ] Document local-only service assumptions.
- [ ] Document TCBS experimental status.
- [ ] Document data-only boundary.
- [ ] Document forbidden APIs.

## 13. Validation

Run:

```bash
ruff check .
ruff format --check .
PYTHONPATH=. pytest tests/unit/core tests/unit/service tests/contracts -q
python -m build --sdist --wheel --no-isolation
```

## Completion checklist

Phase 4 is complete when:

- [ ] auth core exists;
- [ ] credential store abstraction exists;
- [ ] AuthManager exists;
- [ ] TCBS auth is wrapped behind AuthManager;
- [ ] CLI auth commands exist;
- [ ] auth-aware routing exists;
- [ ] local data service exists;
- [ ] Docker runtime exists;
- [ ] no REST login endpoint exists;
- [ ] no account/order/portfolio endpoints exist;
- [ ] service is local/single-user by default;
- [ ] tests pass;
- [ ] docs are updated.
