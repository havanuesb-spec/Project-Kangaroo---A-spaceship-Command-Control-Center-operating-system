# Crystallic Shape Shifting Tool

This is the Multiverse runtime home for the crystallic folder and file reorganizer.

Layout:

- `incoming/`: drop zone for loose files and folders
- `core_geometry/`: routed geometry and lattice material
- `phase_transitions/`: routed transformation and shift material
- `materials/`: routed material and substance notes
- `morphologies/`: routed form-family and variant folders
- `prototypes/`: routed build and prototype assets
- `simulations/`: routed simulation outputs
- `references/`: routed reference files
- `state/`: latest dry-run and apply plan JSON
- `dist/CrystallicReorganizer.exe`: Windows executable

Run:
- `.\multiverse\tools\crystallic_shape_shifting\dist\CrystallicReorganizer.exe`
- `.\multiverse\tools\crystallic_shape_shifting\dist\CrystallicReorganizer.exe --apply`

Default behavior:
- the executable reads from `incoming/`
- it routes files into this folder's crystallic branches
- it writes the latest plan into `state/latest_reorganization_plan.json`
