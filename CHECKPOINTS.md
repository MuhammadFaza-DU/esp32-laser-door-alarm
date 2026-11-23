# CHECKPOINTS: Alarm Pintu ESP32

## Current State (2026-11-23)

- Done / commit: Prototipe meja memakai laser merah terpisah, fotodioda di GPIO34, switch button di GPIO21, dan buzzer lewat KN2222A di GPIO22. Pemilik menguji deteksi cepat dan pembisuan pada firmware 10/60 ms. Sketch, README, foto rangkaian, dan format skematik/simulasi tersimpan di repo.
- In progress: Tidak ada perubahan rangkaian yang sedang berlangsung.
- Blocked: Tidak ada uji di pintu atau konfirmasi tipe fotodioda, tipe dioda pelindung, serta kelas laser unit demo. Pengujian ini tidak dimaksudkan untuk menyatakan kesiapan instalasi.
- Next: Gunakan dokumentasi dan skematik untuk tugas akhir. Jika penempatan, pemancar, atau cahaya ruangan berubah, ukur ulang sebelum menentukan ambang.

## Change Log (newest first)

- 2026-11-23: Mendokumentasikan prototipe meja, menyalin firmware yang diuji, membuat skematik KiCad dan EasyEDA dari model yang sama, menambahkan SVG dan simulasi Wokwi, serta mencatat hasil pengujian.
- 2026-11-19: Menyiapkan Git lokal untuk folder proyek dan mencatat checkpoint dokumentasi awal (`stable-2026-11-19-v1`).
- 2026-11-19: Mencatat aturan proyek, lokasi penggunaan, kebutuhan alarm, dan keputusan desain yang masih terbuka.

## Stable tags (if git)

- `stable-2026-11-19-v1` (lokal): Aturan proyek dan kebutuhan awal sebelum pemilihan sensor. Riwayat publik dimulai dari snapshot terpisah.
