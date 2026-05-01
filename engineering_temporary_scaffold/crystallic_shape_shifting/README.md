# Crystallic Shape Shifting

Purpose:
- hold the working folder hierarchy for crystal-inspired shape-shifting exploration
- separate geometry, phase logic, materials, prototypes, and simulation notes
- keep temporary engineering notes structured without moving the existing top-level materials note yet
- provide a runnable drop-zone reorganizer for loose files and folders

Suggested flow:
1. Drop loose files or folders into `incoming/`.
2. Run `python -m engineering_temporary_scaffold.crystallic_shape_shifting.reorganizer` for a dry run.
3. Run `python -m engineering_temporary_scaffold.crystallic_shape_shifting.reorganizer --apply` when the plan looks right.
4. Use `core_geometry/` for stable forms, lattice ideas, and anchor shapes.
5. Use `phase_transitions/` for rules that describe how one form changes into another.
6. Track candidate substances and constraints in `materials/`.
7. Store variant body plans in `morphologies/`.
8. Put buildable experiments in `prototypes/`.
9. Capture modeled behavior and generated outputs in `simulations/`.
10. Save snapshots and manifests in `state/`.
11. Keep supporting outside notes in `references/`.

Current related note:
- `../Safe Natural Super materials.txt`

Runnable organizer:
- module: `engineering_temporary_scaffold.crystallic_shape_shifting.reorganizer`
- default source: `incoming/`
- default destination: this `crystallic_shape_shifting/` folder
- default mode: dry run, with the latest plan written into `state/latest_reorganization_plan.json`
- test bed: `python -m engineering_temporary_scaffold.crystallic_shape_shifting.test_bed.run_test_bed`
- automated test: `python -m unittest engineering_temporary_scaffold.crystallic_shape_shifting.test_bed.test_reorganizer`
- Windows executable build script: `windows_exe/build_exe.ps1`
- Windows executable output: `windows_exe/dist/CrystallicReorganizer.exe`
