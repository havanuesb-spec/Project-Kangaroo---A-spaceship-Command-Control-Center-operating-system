# Multiverse Trust

This folder is the trust layer for the OS direction of the project.

Files:
- `trust_registry.py`: emits immutable-style JSON trust records with timestamps and integrity hashes.
- `records/`: generated trust records written by the processor and harvester.

Purpose:
- preserve decision provenance
- track generated capabilities
- provide an integrity trail for future policy and capability enforcement
