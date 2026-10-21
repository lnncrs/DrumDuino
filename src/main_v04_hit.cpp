#include <Arduino.h>

const uint8_t PINO_PIEZO_A0 = A0;
const uint8_t PINO_PIEZO_A1 = A1;
const uint8_t PINO_PIEZO_A2 = A2;
const uint8_t PINO_PIEZO_A3 = A3;
const uint8_t PINO_PIEZO_A4 = A4;
const uint8_t PINO_PIEZO_A5 = A5;
const uint8_t PINO_PIEZO_A6 = A6;
const uint8_t PINO_PIEZO_A7 = A7;

const uint8_t PINO_LED = LED_BUILTIN;
const uint8_t SENSOR_ID = 0;

const int LIMIAR = 80;
const unsigned long INTERVALO_BATIDAS_MS = 100;
const unsigned long TEMPO_LED_MS = 40;

unsigned long ultimaBatida = 0;
bool houveBatida = false;
bool ledAceso = false;

void setup()
{
  pinMode(PINO_PIEZO_A0, INPUT);
  pinMode(PINO_PIEZO_A1, INPUT);
  pinMode(PINO_PIEZO_A2, INPUT);
  pinMode(PINO_PIEZO_A3, INPUT);
  pinMode(PINO_PIEZO_A4, INPUT);
  pinMode(PINO_PIEZO_A5, INPUT);
  pinMode(PINO_PIEZO_A6, INPUT);
  pinMode(PINO_PIEZO_A7, INPUT);
  pinMode(PINO_LED, OUTPUT);

  Serial.begin(9600);
}

void loop()
{


  for (uint8_t i = 0; i <= 7; i++)
  {
    const unsigned long agora = millis();
    const int leitura = analogRead(A0 + i);

    const bool podeDisparar =
        !houveBatida ||
        agora - ultimaBatida >= INTERVALO_BATIDAS_MS;

    if (leitura >= LIMIAR && podeDisparar)
    {
      ultimaBatida = agora;
      houveBatida = true;
      ledAceso = true;

      digitalWrite(PINO_LED, HIGH);

      Serial.print("HIT,");
      Serial.print(i);
      Serial.print(",");
      Serial.println(leitura);
    }

    if (ledAceso && agora - ultimaBatida >= TEMPO_LED_MS)
    {
      digitalWrite(PINO_LED, LOW);
      ledAceso = false;
    }
  }

  // const unsigned long agora = millis();
  // const int leitura = analogRead(PINO_PIEZO_A0);

  // const bool podeDisparar =
  //     !houveBatida ||
  //     agora - ultimaBatida >= INTERVALO_BATIDAS_MS;

  // if (leitura >= LIMIAR && podeDisparar)
  // {
  //   ultimaBatida = agora;
  //   houveBatida = true;
  //   ledAceso = true;

  //   digitalWrite(PINO_LED, HIGH);

  //   Serial.print("HIT,");
  //   Serial.print(SENSOR_ID);
  //   Serial.print(",");
  //   Serial.println(leitura);
  // }

  // if (ledAceso && agora - ultimaBatida >= TEMPO_LED_MS)
  // {
  //   digitalWrite(PINO_LED, LOW);
  //   ledAceso = false;
  // }
}