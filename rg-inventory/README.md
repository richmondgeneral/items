# rg-inventory Data

This directory stores label-export artifacts used for printing and ops handoff.

Current source of truth for label data is per-item `RG-XXXX/label.json`,
exported with `npm run labels:build`.

Financial tracking (lot costs, ROI, margin analysis, and inventory tracker spreadsheets)
has moved out of this repository to the private ops repo.

Skill definitions that were previously co-located here were migrated to:
- https://github.com/richmondgeneral/skills
