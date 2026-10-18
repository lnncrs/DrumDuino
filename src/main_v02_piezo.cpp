#include <Arduino.h>

const uint8_t PINO_PIEZO = A0;
const uint8_t PINO_LED = LED_BUILTIN;

const int LIMIAR = 80;
const unsigned long INTERVALO_BATIDAS_MS = 100;
const unsigned long TEMPO_LED_MS = 40;

unsigned long ultimaBatida = 0;
bool houveBatida = false;
bool ledAceso = false;

void setup()
{
  pinMode(PINO_PIEZO, INPUT);
  pinMode(PINO_LED, OUTPUT);

  Serial.begin(9600);
  Serial.println("Teste do piezo: toque no sensor.");
}

void loop()
{
  const unsigned long agora = millis();
  const int leitura = analogRead(PINO_PIEZO);

  const bool podeDisparar =
      !houveBatida ||
      agora - ultimaBatida >= INTERVALO_BATIDAS_MS;

  if (leitura >= LIMIAR && podeDisparar)
  {
    ultimaBatida = agora;
    houveBatida = true;
    ledAceso = true;

    digitalWrite(PINO_LED, HIGH);

    Serial.print("Batida! Leitura: ");
    Serial.println(leitura);
  }

  if (ledAceso && agora - ultimaBatida >= TEMPO_LED_MS)
  {
    digitalWrite(PINO_LED, LOW);
    ledAceso = false;
  }
}