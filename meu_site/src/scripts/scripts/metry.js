let showInterval = false;
let playerIndex = 0; // Índice do jogador principal (será atualizado)

// Função para formatar tempo em minutos:segundos.milisegundos
function formatTime(seconds) {
  if (seconds <= 0 || isNaN(seconds)) return "-";
  const minutes = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(3);
  return `${minutes}:${secs.padStart(6, '0')}`;
}

// Função para formatar gap
function formatGap(gap) {
  if (gap <= 0 || isNaN(gap)) return "0.000";
  return `+${gap.toFixed(3)}`;
}

// Função para carregar dados via API
async function fetchData(endpoint) {
  try {
    const response = await fetch(`http://localhost:5000/api/${endpoint}`);
    return await response.json();
  } catch (error) {
    console.error(`Erro ao carregar ${endpoint}:`, error);
    return [];
  }
}

// Função para atualizar o dashboard
async function updateDashboard() {
  try {
    // Carrega os dados
    const tempos = await fetchData('tempos');
    const telemetria = await fetchData('telemetria');

    // Atualiza o cabeçalho
    document.getElementById('race-mode').textContent = (await fetchData('modo')).modo.toUpperCase();
    document.getElementById('lap').textContent = `LAP ${telemetria.currentLap}/${telemetria.totalLaps}`;

    // Encontra o índice do jogador principal (baseado na telemetria)
    const player = tempos.find(car => car.currentLap === telemetria.currentLap);
    if (player) {
      playerIndex = tempos.indexOf(player);
      document.getElementById('player-name').textContent = player.nome;
      document.getElementById('position').textContent = `POS ${player.position}`;
      document.getElementById('current-position').textContent = player.position;
      document.getElementById('gap-to-leader').textContent = formatGap(player.gapLider);
    }

    // Atualiza a classificação
    const classificationBody = document.getElementById('classification-body');
    const rows = classificationBody.getElementsByTagName('tr');
    for (let i = 0; i < 22; i++) {
      const row = rows[i];
      const car = tempos[i];
      if (car) {
        const gap = showInterval ? car.gapFrente : car.gapLider;
        row.innerHTML = `
          <td class="position">${car.position}</td>
          <td class="driver">${car.nome}</td>
          <td class="gap">${formatGap(gap)}</td>
          <td class="tire tire-${car.tyre}">${car.tyre}</td>
          <td class="penalty">${car.penalty}</td> <!-- Exibe a punição -->
        `;
      } else {
        row.innerHTML = `
          <td class="position">-</td>
          <td class="driver">-</td>
          <td class="gap">-</td>
          <td class="tire">-</td>
          <td class="penalty">-</td>
        `;
      }
    }

    // Atualiza os tempos de volta
    if (player) {
      document.getElementById('current-lap-time').textContent = formatTime(player.currentLapTime || 0);
      document.getElementById('last-lap-time').textContent = formatTime(player.lapTime);
      document.getElementById('best-lap-time').textContent = formatTime(player.bestLapTime || player.lapTime);
    }
    // Atualiza o rodapé (valores mockados para temperatura, já que o backend não fornece)
    document.getElementById('overtake-status').textContent = telemetria.drs ? "ON" : "OFF";
    document.getElementById('track-temp').textContent = "22";
    document.getElementById('air-temp').textContent = "27";
  } catch (error) {
    console.error('Erro ao atualizar dashboard:', error);
  }
}

// Função para alternar entre gap to leader e gap to car ahead
function toggleGapMode() {
  showInterval = !showInterval;
  document.querySelector('.toggle-btn').textContent = showInterval ? "Switch to Delta" : "Switch to Interval";
  updateDashboard();
}

// Atualiza o dashboard a cada 1 segundo
setInterval(updateDashboard, 500);
updateDashboard(); // Carrega inicialmente

udp_thread = Thread(target=coletar_dados_udp, args=(posicoes, track_info, telemetria, track_limits, flag_map, dados_tempos))