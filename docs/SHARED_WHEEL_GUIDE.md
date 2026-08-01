# Shared Wheel Guide

## Kegunaan

Wheel `opticargo-shared` mendistribusikan event/entity/enum/error contract yang sama ke repository consumer. Knowledge Graph menggunakannya untuk memvalidasi DomainEvent dan identifier/schema lintas repository.

## Build dari source resmi

```bash
cd ../opticargo-shared
git fetch --tags
git checkout <TAG_RESMI>
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip build
python -m build --wheel
```

Windows PowerShell menggunakan `py -3.11 -m venv .venv` dan `./.venv/Scripts/Activate.ps1`.

## Verifikasi

- Distribution name `opticargo-shared`.
- Version sesuai contract; implementasi referensi mengunci `1.0.0`, tetapi tag resmi tetap harus dikonfirmasi.
- Wheel berasal dari commit/tag yang dicatat.
- SHA-256 dicatat.
- Import event/entity yang diperlukan berhasil.

## Instalasi offline

Salin wheel yang telah diverifikasi ke `vendor/`, lalu install dengan `python -m pip install vendor/<wheel>.whl`. Wheel tidak masuk Git secara default kecuali policy organisasi menyetujuinya.

URL repository, registry, release page, dan checksum resmi tidak tersedia pada materi yang diberikan dan tidak boleh ditebak.
