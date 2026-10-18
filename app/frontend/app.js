const $ = (id) => document.getElementById(id);
let cursor = 0;
let paused = false;
let rows = [];
let connected = false;

async function api(path, data) {
  const options =
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        };
  const response = await fetch(`/api/${path}`, options);
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "Confira os dados informados.",
    );
  return result;
}

function notice(text, error = false) {
  $("notice").textContent = text;
  $("notice").classList.toggle("error", error);
}

async function refreshPorts() {
  try {
    const ports = await api("ports");
    const selected = $("port").value;
    $("port").replaceChildren(new Option("Selecione a porta", ""));
    for (const item of ports)
      $("port").add(new Option(`${item.port} · ${item.name}`, item.port));
    if (ports.some((item) => item.port === selected))
      $("port").value = selected;
    if (!ports.length)
      notice(
        "Nenhuma porta encontrada. Confira o cabo USB e atualize a lista.",
      );
  } catch (error) {
    notice(error.message, true);
  }
}

function render() {
  $("monitor").textContent = rows.length
    ? rows.join("\n")
    : "Nenhuma mensagem nesta visualização.";
  if ($("scroll").checked) $("monitor").scrollTop = $("monitor").scrollHeight;
}

// A consulta atualiza a tela; a leitura serial continua no backend.
async function update() {
  try {
    const state = await api(`state?after=${cursor}`);
    if (state.total < cursor) {
      cursor = 0;
      rows = [];
    }
    $("audio-status").textContent = state.audio.ready
      ? "Áudio pronto · FluidSynth conectado"
      : state.audio.error || "Áudio indisponível";
    $("audio-mapping").textContent =
      Object.entries(state.audio.mapping)
        .map(([input, note]) => `${input} → nota ${note}`)
        .join(" · ") || "Nenhuma entrada com som configurado";
    connected = Boolean(state.port);
    $("status").textContent = connected
      ? `Conectado · ${state.port}`
      : "Placa desconectada";
    $("status").classList.toggle("online", connected);
    $("connect").disabled = connected;
    $("disconnect").disabled = !connected;
    $("port").disabled = connected;
    $("baud").disabled = connected;
    cursor = state.total;
    $("count").textContent = `${state.total} mensagens recebidas`;
    if (!paused && state.messages.length) {
      rows.push(...state.messages.map((m) => `[${m.time}] ${m.text}`));
      rows = rows.slice(-500);
      render();
    }
    if (state.error) notice(state.error, true);
  } catch {
    $("status").textContent = "Servidor indisponível";
    $("audio-status").textContent = "Sem comunicação com o backend";
    $("status").classList.remove("online");
    $("connect").disabled = true;
    $("disconnect").disabled = true;
    notice(
      "Não foi possível acessar o backend. Confira se o Python está rodando.",
      true,
    );
  } finally {
    setTimeout(update, 250);
  }
}

$("connection-form").onsubmit = async (event) => {
  event.preventDefault();
  $("connect").disabled = true;
  try {
    await api("connect", {
      port: $("port").value,
      baud: Number($("baud").value),
    });
    notice("Placa conectada. A abertura da porta pode reiniciar o Arduino.");
  } catch (error) {
    notice(error.message, true);
  }
};
$("disconnect").onclick = async () => {
  try {
    await api("disconnect", {});
    notice("Porta liberada para outros programas.");
  } catch (error) {
    notice(error.message, true);
  }
};
$("refresh").onclick = refreshPorts;
$("clear").onclick = () => {
  rows = [];
  render();
};
$("pause").onclick = () => {
  paused = !paused;
  $("pause").textContent = paused
    ? "Retomar visualização"
    : "Pausar visualização";
  $("pause").setAttribute("aria-pressed", String(paused));
  $("view-status").textContent = paused
    ? "Visualização pausada. A leitura continua; mensagens deste período não serão exibidas."
    : "Até 500 mensagens na tela. Pausar a visualização mantém a leitura ativa.";
};
refreshPorts();
update();
