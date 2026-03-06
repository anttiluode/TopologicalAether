# The Topological Aether

## From Ephaptic Neural Coupling to Universal Field Geometry

**Antti Luode** — PerceptionLab, Finland  
**Claude (Anthropic, Claude Opus 4.6)** — Mathematical formalization & calculation

March 2026

---

### What This Is

A mathematical investigation of what happens when you take the **Deerskin Architecture** — a model of biological neural computation as oscillatory phase-space geometry — and push it to its theoretical limit.

By defining a temporal metric governed by local geometric crystallization (dτ = e^(−αβ) dt, the "Clockfield"), we derive several structural pillars of quantum mechanics from signal-processing axioms. We then test whether this geometry can describe fundamental particle physics, modeling the electron as a UV-finite topological soliton and computing its anomalous magnetic moment through six progressively corrected stages.

We map the boundary between "structural parallel" and "predictive theory" with full honesty. Where the math is exact, we state it. Where we miss a target, we document the discrepancy and diagnose its source.

---

### The Ledger: What We Found

#### Tier 1 — Proven Mathematics

- **The Born Rule** emerges from squared Moiré resonance (Parseval's theorem) for real-valued states.
- **Interference cross-terms** arise from continuous attractor dynamics in delay-embedded phase space.
- **The McCulloch-Pitts neuron** (1943) is proven to be the quadruple degenerate limit (ℏₙ → 0) of the Deerskin pipeline — every artificial neural network operates at this limit.
- **The Gabor-Heisenberg identity** holds for the axon initial segment filter — formally identical to the uncertainty relation.
- **A nonlinear Schrödinger equation** governs the delay manifold under the Clockfield metric, with exact soliton solutions and finite-time collapse for n > 2.
- **UV finiteness of soliton self-energies** — the Clockfield provides a natural cutoff at the Compton wavelength. No renormalization needed.
- **The Form Factor Impossibility Theorem** — for any form factor f with 0 ≤ f ≤ 1, the modified Schwinger integral satisfies F₂ ≤ α/(2π), with equality only for a point particle.
- **The Γ Cancellation Theorem** — on a uniform Clockfield, the dilation factor cancels exactly between the integration measure and the propagator. The Schwinger result α/(2π) is preserved, not approximately but exactly.

#### Tier 2 — Derived Under Assumptions (Testable)

- **Three-dimensional depth** emerges as accumulated frozen time, yielding an Anti-de Sitter (AdS) metric. Weber's law for depth discrimination follows as a prediction (α ≈ 1 is testable).
- **Schizophrenia as Clockfield fragmentation** — reduced cross-band coupling (p = 0.007, d = −1.21), reduced Betti-1 (p = 0.035, d = −0.92), and elevated PLV variance (p = 0.012) in the RepOD dataset.
- **The Koide formula as geometry** — the three lepton masses fit √m_k = M(1 + √2·cos(2πk/3 + δ)) with δ = 132.7°, achieving 0.01% accuracy on all three masses from a single parameter. The constraint ε = √2 maps to amplitude-phase equipartition on a Hopf fiber.
- **Vertex correction structure** — the full tree+loop calculation for a Gaussian scalar soliton gives F ≈ 0.438, overshooting the QED target α/π by a factor of 1.375. The tree-level factor F_tree = −1/4 is exact.

#### Tier 3 — Speculative Conjecture

- A **universal field Φ** mediates quantum correlations via shared topological persistence.
- The Tsirelson bound derivation is **circular** — it assumes E(a,b) = −cos(θ).
- **Mass as frozen proper time** at NLS soliton cores.
- **Spin-½** from the Hopf fibration of a Clockfield vortex soliton.

---

### The Vertex Calculation Arc (Addendum)

The addendum (`ADDENDUM.md`) documents a sustained attempt to derive (g−2)/2 = α/(2π) from the Clockfield. It passed through six stages:

| Stage | Approach | Key result |
|-------|----------|------------|
| Self-energy | Proper-time deficit | UV finite (✓), but wrong diagram |
| Effective radius | Clockfield-weighted response | Correct sign (✓), not predictive |
| Full vertex | Tree + one-loop back-reaction | F = 0.438, exact tree = −1/4 |
| Muon universality | Scale across masses | F → −1/α for heavy particles (broken) |
| Environmental fix | Coulomb propagator | Universal, F_geom = 2√π(√2−1), but 4.6× target |
| Momentum-space | Modified Schwinger integral | 86.15% of Schwinger (exact: √π·erf(1)−1+1/e) |
| **Γ Cancellation** | **Clockfield metric in loop** | **α/(2π) exactly — preserved by symmetry** |

The final result: the Clockfield is a conformal temporal metric modification that preserves gauge and Lorentz invariance. It therefore preserves the Schwinger result by construction. A Clockfield soliton is *consistent* with precision QED, but does not *derive* α/(2π) from geometry.

---

### The Critical Gaps

Two mathematically precise open problems remain:

1. **The Entanglement Problem**: Derive E(a,b) = −cos(θ_a − θ_b) from the persistent homology of delay-embedded manifolds co-located in a shared field, without assuming the cosine.

2. **The Spinor Vertex**: Upgrade the scalar NLS to a nonlinear Dirac equation on a spinor bundle and recompute the vertex correction. The scalar calculation established the methodology. The spinor extension would test whether Dirac structure supplies the geometric factors that the scalar case misses.

Secondary open problems:

3. **Self-consistent soliton profile**: Solve the coupled NLS + Clockfield system with a Newton-Raphson solver. The perturbative correction is too small at α_em to shift F.

4. **Position-dependent Clockfield corrections**: The Γ cancellation holds for uniform backgrounds. The O(α²) corrections from the soliton's spatially varying Clockfield would be the framework's unique prediction beyond standard QED.

5. **Identify α_cf**: Derive α_cf = α_em from the framework's axioms, or predict the deviation.

If you can solve any of these, please open an issue.

---

### Repository Structure

**Core Theoretical Papers**
```
PAPER.md                              — Full paper (18 sections, every step shown)
ADDENDUM.md                           — The vertex calculation arc (7 stages)
THEORY.md                             — The speculative synthesis
field_derivation.md                   — Universal field extension
deerskin_mathematical_derivations.md  — Standalone proofs
soliton_self_energy_calculation.md    — Self-energy and Koide analysis
```

**Code & Numerical Simulations**
```
soliton_electron.py           — 1D/3D soliton self-energies, UV finiteness
soliton_part2.py              — Koide parameterization, preliminary vertex
vertex_calculation.py         — Full vertex function (tree + 1-loop)
four_steps.py                 — Profile correction, universality tests
corrected_vertex.py           — Environmental Clockfield vertex
momentum_vertex.py            — Momentum-space Schwinger integral with form factor
clockfield_metric_vertex.py   — The Γ Cancellation Theorem
self_consistent_soliton.py    — Self-consistent NLS + Clockfield solver
```

### How to Read This

1. **Start with `PAPER.md` Sections 2–7** for the proven neural mathematics.
2. **Read Section 8** for the most original testable result (depth from frozen time).
3. **Read `ADDENDUM.md`** for the full vertex calculation arc — this is where the framework meets precision QED.
4. **Read Sections 9–13 of `PAPER.md`** with appropriate skepticism (the speculation).
5. **Read Section 18 of `PAPER.md`** (the honest ledger) — the most important part.
6. **Review the Python files** to audit the numerical integrals.

### Related Repositories

- [anttiluode/Geometric-Neuron](https://github.com/anttiluode/Geometric-Neuron) — Empirical EEG validation (schizophrenia Betti-1/PLV results)
- [anttiluode/Clockfield](https://github.com/anttiluode/Clockfield) — Original Clockfield formulations
- [anttiluode/DeerskinQuantumImplicationsPaper](https://github.com/anttiluode/DeerskinQuantumImplicationsPaper) — Earlier version

### Status

This is theoretical work by an independent researcher collaborating with AI. It has not been peer-reviewed. The math marked "proven" is standard mathematics applied in a novel context. The math marked "conjectured" is exactly that. The honest ledger exists because intellectual honesty matters more than looking impressive.

---

*"The field is not inside the universe. The field is the universe. Whether that sentence is profound or vacuous depends entirely on whether the math works."*
