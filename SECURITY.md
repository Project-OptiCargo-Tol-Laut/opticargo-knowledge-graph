# Security

Jangan commit `.env`, token, credential, raw payment data, secret provider, atau PII nyata. Event payload, DLQ, log, metric label, dan graph property harus menggunakan allowlist serta redaction. Query parameter wajib dipisahkan dari identifier/schema token agar tidak membuka Cypher injection. Kanal pelaporan privat belum tercantum pada materi proyek dan harus ditentukan oleh pemilik organisasi.
