# 📜 DentalAi — Changelog & Release Notes

## [1.0.0] - 2026-08-11

### 🚀 Major Improvements & Audit Fixes (Batches 23–32)

#### 🔴 Critical Geometry & Format Fixes (Audit Category A)
- **A.1:** Fixed TypeScript type error in `AgentSwarmLogger.tsx` (`action: string;`).
- **A.2:** Implemented actual boolean difference `trimesh.boolean.difference` for resin drain holes in `model_builder.py`.
- **A.3:** Included inspection windows (`win`) in surgical guide assembly `guide_parts` in `guide_builder.py`.
- **A.4:** Included ASC screw channel in custom abutment concatenation in `abutment_generator.py`.
- **A.5:** Added `fdi` and `order_id` parameters to `compile_5axis_gcode` in `cam_engine.py` for legitimate MDR G-code program headers.
- **A.6:** Connected real `margin_curve_json` and `insertion_axis_json` parsing in `generate_cam_metadata` in `mcp/server.py`.
- **A.7:** Extracted dynamic patient, doctor, and clinic data from real `Order` entities in `generate_mdr_passport` in `mcp/server.py`.
- **A.8 & A.9:** Connected `ConnectionManager.broadcast_log()` and FastAPI startup background task for `OrderIngestionService` hot-folder watching.

#### 🔴 Geometry Measurements & Determinism (Audit Category B)
- **B.1 & F.3:** Replaced `np.random.randn()` with deterministic mesh measurement in `qa_inspector.py`.
- **B.3:** Calculated connector cross-section area dynamically in `bridge_generator.py`.
- **B.6:** Dynamically assigned `target_prep_fdi` and adjacent teeth in `segmenter.py`.

#### 🟠 Security & Control-Plane (Audit Category D & Reviewer.md)
- **Reviewer.md:** Created `evolution/policy/protected_paths.yaml`, `risk_classification.yaml`, and `CODEOWNERS` defining Zone R (Regulated Core) & Zone P (Policy) boundaries.
- **D.1:** Restricted CORS origins to explicit localhost origins in `main.py`.
- **D.2 & G.6:** Created `.env.example` with safe environment defaults.
- **F.1:** Added Pydantic field validator for FDI numbers against `FDI_TOOTH_MAP` (11–48).

#### 🟡 Frontend & Production Build (Audit Category E & J)
- **E.2 & E.3:** Fixed header label in `Viewport3D.tsx` to `"3D CAD/CAM Viewport"`.
- **J.3:** Added interactive `onClick` handlers for intervention buttons in `AgentSwarmLogger.tsx`.
- **J.4:** Added `aria-label` accessibility attributes to SVGs in `TelemetryDock.tsx`.
- **Next.js:** Clean production build (`npm run build`) verified with zero errors.
