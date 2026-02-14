# rg-inventory Data

This directory stores legacy inventory data artifacts
(e.g. historical label sheets and tracker spreadsheets).

Current source of truth for label data is per-item `RG-XXXX/label.json`,
exported with `npm run labels:build`.

Planned state: move these operational artifacts to a dedicated ops repository
and keep this repo focused on deployable site content plus item-level metadata.

Skill definitions that were previously co-located here were migrated to:
- https://github.com/richmondgeneral/skills
