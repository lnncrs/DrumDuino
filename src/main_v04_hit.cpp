#include <Arduino.h>

const uint8_t PINOS_PIEZO[] = {A0, A1, A2, A3, A4, A5, A6, A7};
const uint8_t NUM_SENSORES = sizeof(PINOS_PIEZO) / sizeof(PINOS_PIEZO[0]);

// Habilite somente os canais com piezo conectado. Entradas soltas captam ruido.
const bool SENSOR_HABILITADO[NUM_SENSORES] = {
    true, true, true, true, true, false, false, false};

const uint8_t PINO_LED = LED_BUILTIN;
const uint8_t SENSOR_ID = 0;

const int LIMIAR = 150;
const unsigned long INTERVALO_BATIDAS_MS = 300;
const unsigned long TEMPO_LED_MS = 40;

unsigned long ultimaBatida[NUM_SENSORES] = {};
bool houveBatida[NUM_SENSORES] = {};
unsigned long ultimoAcendimentoLed = 0;
bool ledAceso = false;

void setup()
{
  // A6 e A7 no Nano sao exclusivamente analogicos; analogRead dispensa pinMode.
  pinMode(PINO_LED, OUTPUT);
  Serial.begin(9600);
}

void loop()
{
  for (uint8_t i = 0; i < NUM_SENSORES; i++)
  {
    if (!SENSOR_HABILITADO[i])
    {
      continue;
    }

    const int leitura = analogRead(PINOS_PIEZO[i]);
    const unsigned long agora = millis();
    const bool podeDisparar =
        !houveBatida[i] ||
        agora - ultimaBatida[i] >= INTERVALO_BATIDAS_MS;

    if (leitura >= LIMIAR && podeDisparar)
    {
      ultimaBatida[i] = agora;
      houveBatida[i] = true;
      ultimoAcendimentoLed = agora;
      ledAceso = true;
      digitalWrite(PINO_LED, HIGH);

      Serial.print("HIT,");
      Serial.print(i);
      Serial.print(",");
      Serial.println(leitura);
    }
  }

  if (ledAceso && millis() - ultimoAcendimentoLed >= TEMPO_LED_MS)
  {
    digitalWrite(PINO_LED, LOW);
    ledAceso = false;
  }
}
