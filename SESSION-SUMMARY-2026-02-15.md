# Session Summary — 2026-02-15

## 1) Commit review and bug fixes

- Reviewed recent commits and validated with existing checks.
- Fixed price tracking mismatch in `RG-0008/index.html` (`price: 29.99` -> `price: 30`).
- Added missing `RG-0015/label.json` so label export works.
- Synced active item label prices (`RG-0001`..`RG-0014`) to match current storefront pricing.
- Re-ran checks:
  - `npm run -s ui:test`
  - `npm run -s labels:build`
  - targeted consistency checks for label/UI/track-event alignment

## 2) Category/filter validation on local storefront

- Verified `index.html` filter buttons match all `data-category` values.
- Confirmed runtime filtering behavior with Playwright click test.
- Preserved visual category names as requested.

## 3) Live Square storefront audit

- Queried live Square Online storefront and exported current product/category snapshots to:
  - `qa-artifacts/square-catalog/live-catalog-2026-02-15T16-23-46Z.json`
  - `qa-artifacts/square-catalog/live-catalog-2026-02-15T16-23-46Z.csv`
  - `qa-artifacts/square-catalog/live-catalog-summary-2026-02-15T16-23-46Z.json`
- Reported category usage and uncategorized items from public feed.

## 4) Cowork handoff verification and publish path

- Verified cowork “push-ready” claim and found blocking issues in `RG-0016`..`RG-0020`:
  - missing `label.json`
  - missing `qr-code.png` (only `qr.png`)
  - unresolved `{{PLACEHOLDERS}}` token
  - gallery links referencing `hero.jpeg` while files were `hero.png`
- Applied minimal fixes for deployability:
  - updated hero references to `.png` in item pages and gallery cards
  - added `label.json` files for `RG-0016`..`RG-0020`
  - created `qr-code.png` from existing `qr.png`
  - removed placeholder token match that failed validation
- Re-ran `validate-item.sh` for all five items (pass with warnings).

## 5) Git lock and push

- `git add` was blocked by stale `.git/index.lock`.
- Resolved by moving lock file to `.git/index.lock.stale`.
- Staged intended DVD batch files and committed:
  - commit: `b8548de`
  - message: `Add RG-0016 through RG-0020: 5 DVD batch from Dan flea market lot`
- Push initially rejected due to remote advancing; rebased onto latest `origin/main` and pushed successfully.

## 6) Skill/refactor investigation

- Compared key skills between:
  - `~/.codex/skills/...`
  - `~/.claude/skills/...`
- Verified no substantive content diffs for:
  - `rg-full-auto`
  - `rg-item-update`
  - `catalog-classifier`
  - `square-image-upload`
  - `square-cache`
  - `image-processor`
- Conclusion: not a lost-skill-content issue in these files.

## 7) Claude Desktop MCP state check

- Confirmed current active config:
  - `~/Library/Application Support/Claude/claude_desktop_config.json`
- Current MCP server keys:
  - `mcp_square_api`
  - `alpaca`
  - `square_cache_mcp`
- Confirmed referenced backup exists and contains older key naming (`RGSquareItemCache`).

## 8) MCP hardening, env flattening, and restart verification

- Standardized runtime around Astral `uv` install path (`~/.local/bin/uvx`) and removed ambiguity from mixed install locations.
- Consolidated environment handling to one canonical file:
  - `~/.config/claude-mcp/.env`
- Preserved dual-Square architecture by intent:
  - `mcp_square_api` = official remote OAuth server (no local key injection)
  - `square_cache_mcp` = custom Richmond General cache server
- Simplified local server launch paths with explicit wrappers:
  - `~/.config/claude-mcp/bin/start-alpaca-mcp.sh`
  - `~/.config/claude-mcp/bin/start-square-cache-mcp.sh`
- Updated Claude Desktop MCP config to use wrapper commands for local servers and kept remote OAuth server via `npx mcp-remote`.
- Investigated load errors in:
  - `~/Library/Logs/Claude/mcp.log`
  - `~/Library/Logs/Claude/mcp-server-mcp_square_api.log`
  - `~/Library/Logs/Claude/main.log`
  - `~/Library/Logs/Claude/claude.ai-web.log`
- Root finding:
  - `alpaca` and `square_cache_mcp` were healthy and initialized cleanly.
  - Remote `mcp_square_api` showed repeated `http-first` 404 fallback churn before SSE connect.
- Applied transport tuning for stability/noise reduction:
  - `mcp_square_api.args` -> `["mcp-remote","https://mcp.squareup.com/sse","--transport","sse-first"]`
- Restarted Claude Desktop and verified in logs that new sessions use `sse-first` and connect via `SSEClientTransport`.
- Created timestamped config backup for this transport change:
  - `~/.codex-backups/mcp-square-transport-20260215-090757/`
