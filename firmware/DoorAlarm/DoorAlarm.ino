const int PIN_FOTODIODA = 34;
const int PIN_SWITCH = 21;
const int PIN_BUZZER = 22;

const int AMBANG_MV = 1500;
const unsigned long WAKTU_PUTUS_MS = 10;
const unsigned long WAKTU_BALIK_MS = 60;

enum Status { TUNGGU_BERKAS, SIAP, ALARM };
Status status = TUNGGU_BERKAS;

bool berkasTerdeteksi = false;
bool bacaanSebelumnya = false;
bool switchSebelumnya = false;
unsigned long waktuBacaanBerubah = 0;

void setup() {
  pinMode(PIN_SWITCH, INPUT);  // Pull-up eksternal 10 kΩ ke 3V3.
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
}

void loop() {
  unsigned long sekarang = millis();
  bool bacaanBerkas = analogReadMilliVolts(PIN_FOTODIODA) >= AMBANG_MV;

  if (bacaanBerkas != bacaanSebelumnya) {
    bacaanSebelumnya = bacaanBerkas;
    waktuBacaanBerubah = sekarang;
  }

  unsigned long waktuStabil = bacaanBerkas ? WAKTU_BALIK_MS : WAKTU_PUTUS_MS;
  if (sekarang - waktuBacaanBerubah >= waktuStabil) {
    berkasTerdeteksi = bacaanBerkas;
  }

  bool switchDipencet = digitalRead(PIN_SWITCH) == LOW;
  bool baruDipencet = switchDipencet && !switchSebelumnya;
  switchSebelumnya = switchDipencet;

  switch (status) {
    case TUNGGU_BERKAS:
      if (berkasTerdeteksi) status = SIAP;
      break;

    case SIAP:
      if (!berkasTerdeteksi) status = ALARM;
      break;

    case ALARM:
      if (baruDipencet) {
        status = berkasTerdeteksi ? SIAP : TUNGGU_BERKAS;
      }
      break;
  }

  digitalWrite(PIN_BUZZER, status == ALARM ? HIGH : LOW);
  delay(5);
}
