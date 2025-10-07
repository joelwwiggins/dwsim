# DWSIMpy Frontend Refactor & MCP Integration

## Overview
This document summarizes the refactor of the Svelte-based flowsheet UI and how to leverage the Svelte MCP server for enhanced developer workflows.

## Goals
- Separate concerns (types, API, stores, serialization, constants)
- Enable testability & maintainability
- Provide a single source of truth for unit operations
- Support richer backends transparently
- Add groundwork for validation, persistence, and MCP-assisted automation

## Module Layout
```
src/lib/types/flowsheet.ts        # Shared type definitions
src/lib/api/client.ts             # API base resolution, health polling, requests
src/lib/serialization/flowsheet.ts# Payload builder for simulation
src/lib/stores/flowsheet.ts       # State & operations (nodes, edges, simulation)
src/lib/constants/unitTypes.ts    # Unit metadata (deduplicated)
```

## Key Stores
- `nodes`, `edges`: Canonical flowsheet elements
- `simulationResults`: Latest result payload
- `notifications`: User feedback events
- `connectionState`: Backend availability (polled)

## Running a Simulation (New Flow)
1. UI triggers `runSimulation()` from `stores/flowsheet.ts`
2. Payload built via `buildSimulationPayload()`
3. Calls `api.loadFlowsheet()` then `api.runSimulation()`
4. Results stored in `simulationResults`

## Advantages of Refactor
| Concern | Before | After |
|---------|--------|-------|
| API coupling | Inline `fetch` in page | Centralized in `api/client.ts` |
| Node/Edge shape | Implicit & ad-hoc | Explicit via `types/flowsheet.ts` |
| Unit list | Duplicated w/ duplicates | Single `unitTypes` constant |
| Simulation orchestration | Inline in page | Reusable store function |
| Extensibility | Harder to add new backends | Base override via store |
| Observability | Console only | Notifications + connection state |

## MCP Integration Ideas
Using the Svelte MCP server (configured in `mcp.json`):

### Potential Commands
- `svelte.docs.section` → On-demand docs for specific concepts (slots, stores, transitions)
- `flowsheet.audit` → Custom command to:
  - Detect duplicate node IDs
  - Report unconnected unit operations
  - Suggest missing properties
- `flowsheet.scaffold.unit <name>` → Generate new unit editor component template
- `api.verify` → Cross-check front-end payload keys vs backend endpoints (future introspection route)

### Developer Workflow Example
1. Add new unit type in `unitTypes.ts`
2. Run MCP command: `flowsheet.scaffold.unit distillation_reboiler`
3. Command returns component stub + store enhancer suggestion
4. Use docs command to display recommended Svelte patterns for dynamic forms

## Extending Backend Awareness
Add endpoint `/api/capabilities` (future) returning:
```json
{
  "propertyPackages": ["ideal", "peng-robinson"],
  "unitOperations": ["heater", "mixer", "compressor"],
  "features": {"save": true, "load": true}
}
```
Then adapt palette dynamically instead of static `unitTypes` list.

## Next Steps
1. Add persistence (localStorage or backend save/load wiring)
2. Implement notification toaster UI
3. Introduce Vitest + Playwright smoke test
4. Add accessibility auditing (role/aria checks)
5. Generate type guards for distinguishing stream vs unit nodes
6. Integrate MCP custom commands for audits & scaffolding

## Migration Notes
- Existing flowsheet interactions remain; state now lives in stores.
- Replace any direct mutations (`nodes = ...`) with store operations.
- Legacy utilities can be moved under `lib/utils/` as needed.

## Quick Usage Snippets
```ts
import { addUnitNode, addStreamNode, runSimulation } from '$lib/stores/flowsheet';
addUnitNode('heater');
addStreamNode();
await runSimulation();
```

## Troubleshooting
| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| API base incorrect | Non-standard port mapping | Manually set `apiBase.set('http://host:port/api')` |
| Simulation empty results | Backend simplified stub | Switch to full backend implementation |
| Duplicate edges | Missing guard | Add check in `connectNodes()` (future) |

---
Refactor complete. Future enhancements can build atop this modular structure with minimal churn.
