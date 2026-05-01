# Multiverse Capabilities

This folder is the capability layer for the OS direction of the project.

Files:
- `mathematics_identifier.py`: classifies math-oriented requests into a likely algorithm family.
- `processor.py`: normalizes requests, creates a structured processing decision, and generates a capability module.
- `harvester.py`: writes generated capability code into the capability layer and registers a trust record.
- `bootstrap.py`: example entry point that runs the pipeline.

Flow:
1. A prompt enters the processor.
2. The processor normalizes input and fingerprints the prompt.
3. The mathematics identifier selects a likely algorithm family.
4. The processor creates a decision record with confidence, evidence, and execution mode.
5. The harvester writes a generated module and emits a harvest trust record.
