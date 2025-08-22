# ADR 0001 — PairCoder Context Loop

**Status:** Accepted
**Context:** AI agents operate with limited context windows and benefit from a compact, structured state that is continuously maintained by developers.
**Decision:** We maintain a persistent context loop in `context/development.md` with four fields:

- **Overall goal is:** one-sentence mission
- **Last action was:** the latest material change
- **Next action will be:** the immediate next step
- **Blockers:** any impediments or decisions needed

**Consequences:**
- Agents read stable state every session.
- Developers must update after each change (`bpsai-pair context-sync`).
- Context packs exclude heavy assets; agents assume excluded assets exist.