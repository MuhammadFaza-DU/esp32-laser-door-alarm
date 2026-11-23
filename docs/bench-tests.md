# Catatan pengujian meja

Pengukuran berikut berasal dari satu prototipe. Angkanya bukan spesifikasi umum komponen atau jaminan performa di pintu.

| Pengujian | Hasil |
|---|---|
| GPIO21, switch button dilepas | Sekitar **3,2 V**. |
| GPIO21, switch button dipencet | **0,08–0,10 V** pada pengukuran ulang. |
| VIN dari USB-C | **4,53 V** tanpa beban buzzer; sekitar **4,5 V** saat buzzer langsung berbunyi. |
| IRFZ44N dengan kontrol 3,3 V | Buzzer tidak bunyi. Terminalnya terbaca **4,53 V** dan **3,72 V** terhadap GND, sehingga hanya ada **0,81 V** di buzzer. Tegangan kontrol yang dilaporkan **3,12 V**. |
| KN2222A dengan resistor basis 680 Ω | Tes mati dan nyala lulus menurut pemilik proyek. Setelah GPIO22 dipakai untuk kontrol, uji switch button dan buzzer lewat sketch tes juga lulus. |
| Fotodioda, multimeter | **0,01 V** ditutup, **0,03 V** dengan cahaya ruangan, dan hingga **sekitar 2,2 V** saat disenterin pada pengujian terpisah. |
| Fotodioda, Serial Monitor saat uji berkas | Rekaman menunjukkan pembacaan berulang **142 mV** dan **3171 mV**. Nilai tinggi mungkin sudah mendekati batas ADC. |
| Firmware 10/60 ms | Pemilik melaporkan bahwa gerakan cepat terdeteksi dan switch button membisukan buzzer. Belum ada pengukuran waktu respons atau pengujian di pintu. |

## Kalau hasilnya berbeda

- **GPIO21 tidak tinggi saat switch button dilepas:** ukur sisi `3V3` dari resistor 10 kΩ, lalu pastikan sisi satunya benar-benar sebaris dengan GPIO21. Matikan daya sebelum mengubah posisi kabel.
- **Buzzer diam:** ukur tegangan langsung di kedua kakinya saat alarm aktif. Mengukur satu kaki terhadap GND saja tidak menunjukkan tegangan yang diterima buzzer. Cek urutan E–B–C untuk KN2222A yang digunakan.
- **Sensor tidak berubah:** ukur GPIO34 terhadap GND dengan probe hitam di GND. Bandingkan bacaan saat ditutup dengan benda buram dan saat kena cahaya. Bedakan **V** dan **mV**. Jangan hubungkan sinyal di luar rentang 0–3,3 V ke GPIO34.
- **Alarm melewatkan gerakan cepat:** filter butuh bacaan rendah yang bertahan 10 ms pada pembacaan berkala. Lebar benda, arah geraknya, dan frekuensi sampling memengaruhi apakah peristiwa sempat terbaca.

## Cek ulang tanpa mem-flash board

Jalankan dari root repo:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/DoorAlarm
g++ -std=c++17 -Wall -Wextra -Werror tests/door_alarm_test.cpp -o door-alarm-test
./door-alarm-test
python tests/check_schematics.py
```

Di Windows gunakan `-o door-alarm-test.exe` dan jalankan `.\door-alarm-test.exe`. Tes C++ menjalankan sketch yang sama dengan masukan sensor serta waktu buatan. Ini memeriksa logika startup, filter, alarm yang tetap aktif, pembisuan, dan kesiapan ulang. Tes bukan pengganti pengujian perangkat fisik.

Skematik KiCad dibuka di KiCanvas dan JSON diimpor ke EasyEDA Standard. Tes Python membandingkan sambungan di kedua format dengan rangkaian fisik. Pemeriksaan ini bukan ERC dari aplikasi desktop KiCad.

Pada uji Wokwi di browser, LED menyala saat potensiometer diturunkan, tetap menyala saat dinaikkan, padam saat sakelar virtual digeser, dan menyala lagi pada pemutusan berikutnya. Uji ini tidak mengukur respons rangkaian fisik.
