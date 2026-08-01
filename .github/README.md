# GitHub Configuration

Folder ini menyediakan template governance repository. Workflow sengaja menggunakan ekstensi `.disabled` sampai command build, migration, test, image, dan artifact benar-benar tersedia.

## Aktivasi workflow

Workflow baru dapat diaktifkan setelah:

- dependency dan Shared wheel source disepakati;
- lint, type-check, unit, contract, architecture, migration-resource, dan packaging test berjalan nyata;
- integration job memiliki service dependency serta cleanup;
- image mempunyai healthcheck dan non-root runtime;
- secret scanning dan artifact provenance ditentukan.
