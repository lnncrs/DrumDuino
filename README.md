# DrumDuino

**Projeto de bateria eletrônica com Arduino**

![UFABC Logo](assets/logotipo-ufabc-extenso.png)

Universidade Federal do ABC - Bacharelado em Ciência e Tecnologia<br />
Disciplina e quadrimestre a confirmar

Lenin Cristi<br />
lenin.cristi@aluno.ufabc.edu.br

## Resumo

O DrumDuino é um projeto didático voltado ao desenvolvimento de uma bateria eletrônica com Arduino. O firmware é escrito em C++ com o framework Arduino e organizado com PlatformIO, com configuração para a placa Arduino Nano com ATmega328.

O projeto está na etapa inicial de configuração e validação da placa. Atualmente, o firmware configura o LED integrado como saída e alterna entre ligado e desligado a cada 500 ms. A leitura dos sensores, o processamento das batidas e a saída musical ainda não estão implementados; os componentes e as conexões da bateria serão definidos nas próximas etapas.

## Estrutura do projeto

```text
.
├── assets/                     # Identidade visual
├── src/
│   └── main.cpp                # Firmware Arduino; teste inicial do LED
├── include/                    # Diretório reservado para cabeçalhos
├── lib/                        # Diretório reservado para bibliotecas do projeto
├── test/                       # Diretório reservado para testes
├── .vscode/                    # Configurações do ambiente de desenvolvimento
├── platformio.ini              # Placa, plataforma, framework e monitor serial
├── .gitignore                  # Artefatos do PlatformIO e arquivos locais do editor
└── LICENSE                     # Licença MIT
```

## Ambiente de desenvolvimento

- Arduino Nano com ATmega328 e cabo USB compatível.
- PlatformIO instalado, por exemplo pela extensão PlatformIO IDE no Visual Studio Code.
- Framework Arduino e plataforma `atmelavr`, definidos em `platformio.ini`.

O ambiente configurado é `nanoatmega328`. A velocidade do monitor serial está definida como 9600 baud, mas o firmware atual ainda não envia mensagens pela serial.

## Como executar

1. Abra a pasta do projeto no PlatformIO.
2. Conecte a placa ao computador por USB.
3. Compile o firmware pela opção **Build**.
4. Grave o firmware na placa pela opção **Upload**.
5. Confira se o LED integrado permanece aceso por 500 ms e apagado por 500 ms, repetidamente.

Se o comando `pio` estiver disponível no terminal, a compilação e a gravação também podem ser feitas com:

```sh
pio run -e nanoatmega328
pio run -e nanoatmega328 -t upload
```

## Licença

O código deste projeto é disponibilizado sob a [licença MIT](LICENSE).

___

CMCC - Universidade Federal do ABC (UFABC) - Santo André - SP - Brasil
