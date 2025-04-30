
let pilots = [];
let trackPath = [];
let pilotData = {};
let speedChart, throttleChart, brakeChart;
const canvas = document.getElementById('trackCanvas');
const ctx = canvas.getContext('2d');

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

// Função para atualizar o seletor de eventos com base na temporada
async function updateEventSelector() {
  const seasonSelect = document.getElementById('season');
  const eventSelect = document.getElementById('event');
  eventSelect.innerHTML = '<option value="">Select Event</option>';

  if (seasonSelect.value) {
    // Aqui você pode adicionar uma lógica para buscar eventos de uma temporada
    // Como o backend atual não suporta isso, vou mockar alguns eventos
    const events = [
      { id: 0, name: "Melbourne" },
      { id: 3, name: "Spa" },
      { id: 4, name: "Bahrain" }
    ];
    events.forEach(event => {
      const option = document.createElement('option');
      option.value = event.id;
      option.textContent = event.name;
      eventSelect.appendChild(option);
    });
  }
  updateSessionSelector();
}

// Função para atualizar o seletor de sessões
async function updateSessionSelector() {
  const eventSelect = document.getElementById('event');
  const sessionSelect = document.getElementById('session');
  sessionSelect.innerHTML = '<option value="">Select Session</option>';

  if (eventSelect.value) {
    // Mock de sessões (Qualifying, Race, etc.)
    const sessions = ["Qualifying", "Race"];
    sessions.forEach(session => {
      const option = document.createElement('option');
      option.value = session.toLowerCase();
      option.textContent = session;
      sessionSelect.appendChild(option);
    });
  }
  updatePilotSelector();
}

// Função para carregar pilotos
async function updatePilotSelector() {
  const sessionSelect = document.getElementById('session');
  const pilot1Select = document.getElementById('pilot1');
  const pilot2Select = document.getElementById('pilot2');
  pilot1Select.innerHTML = '<option value="">Select Pilot 1</option>';
  pilot2Select.innerHTML = '<option value="">Select Pilot 2</option>';

  if (sessionSelect.value) {
    const tempos = await fetchData('tempos');
    const posicoesData = await fetchData('posicoes');
    trackPath = posicoesData.path || [];

    pilots = tempos.map((car, index) => ({
      index: index,
      name: car.nome,
      currentLap: car.currentLap
    }));

    pilots.forEach(pilot => {
      const option1 = document.createElement('option');
      const option2 = document.createElement('option');
      option1.value = pilot.index;
      option2.value = pilot.index;
      option1.textContent = pilot.name;
      option2.textContent = pilot.name;
      pilot1Select.appendChild(option1);
      pilot2Select.appendChild(option2);
    });

    if (pilots.length > 0) pilot1Select.value = pilots[0].index;
    if (pilots.length > 1) pilot2Select.value = pilots[1].index;

    updateLapSelector('pilot1', 'lap1');
    updateLapSelector('pilot2', 'lap2');
  }
}

// Função para atualizar o seletor de voltas
async function updateLapSelector(pilotSelectId, lapSelectId) {
  const pilotSelect = document.getElementById(pilotSelectId);
  const lapSelect = document.getElementById(lapSelectId);
  const pilotIndex = parseInt(pilotSelect.value);

  lapSelect.innerHTML = '<option value="">Select Lap</option>';

  if (!isNaN(pilotIndex)) {
    const data = await fetchData(`telemetria_volta/${pilotIndex}/${pilotIndex}`);
    const pilotData = data.piloto1;
    const availableLaps = Object.keys(pilotData.laps).sort((a, b) => b - a);

    availableLaps.forEach(lap => {
      const option = document.createElement('option');
      option.value = lap;
      option.textContent = `Lap ${lap}`;
      lapSelect.appendChild(option);
    });

    if (availableLaps.length > 0) {
      lapSelect.value = availableLaps[0];
    }
  }

  updateMapAndGraphs();
}

// Função para normalizar coordenadas do traçado
function normalizeCoordinates(x, z, canvasWidth, canvasHeight) {
  const minX = Math.min(...trackPath.map(p => p[0]));
  const maxX = Math.max(...trackPath.map(p => p[0]));
  const minZ = Math.min(...trackPath.map(p => p[1]));
  const maxZ = Math.max(...trackPath.map(p => p[1]));

  const xRange = maxX - minX;
  const zRange = maxZ - minZ;
  const scale = Math.min(canvasWidth / xRange, canvasHeight / zRange) * 0.8;

  const normalizedX = (x - minX) * scale + (canvasWidth - xRange * scale) / 2;
  const normalizedZ = (z - minZ) * scale + (canvasHeight - zRange * scale) / 2;

  return [normalizedX, canvasHeight - normalizedZ];
}

// Função para encontrar a posição no traçado
function getPositionOnTrack(lapDistance) {
  if (!trackPath.length) return [0, 0];

  let totalLength = 0;
  for (let i = 0; i < trackPath.length - 1; i++) {
    const [x1, z1] = trackPath[i];
    const [x2, z2] = trackPath[i + 1];
    totalLength += Math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2);
  }

  const normalizedDistance = (lapDistance % totalLength) / totalLength;
  const trackSegment = normalizedDistance * (trackPath.length - 1);
  const segmentIndex = Math.floor(trackSegment);
  const segmentFraction = trackSegment - segmentIndex;

  const [x1, z1] = trackPath[segmentIndex];
  const [x2, z2] = trackPath[Math.min(segmentIndex + 1, trackPath.length - 1)];
  const x = x1 + (x2 - x1) * segmentFraction;
  const z = z1 + (z2 - z1) * segmentFraction;

  return normalizeCoordinates(x, z, canvas.width, canvas.height);
}

// Função para formatar tempo
function formatTime(seconds) {
  if (seconds <= 0 || isNaN(seconds)) return "0:00.000";
  const minutes = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(3);
  return `${minutes}:${secs.padStart(6, '0')}`;
}

// Função para atualizar o mapa e os gráficos
async function updateMapAndGraphs() {
  const pilot1Select = document.getElementById('pilot1');
  const pilot2Select = document.getElementById('pilot2');
  const lap1Select = document.getElementById('lap1');
  const lap2Select = document.getElementById('lap2');
  const pilot1Index = parseInt(pilot1Select.value);
  const pilot2Index = parseInt(pilot2Select.value);
  const lap1 = parseInt(lap1Select.value);
  const lap2 = parseInt(lap2Select.value);

  if (isNaN(pilot1Index) || isNaN(pilot2Index) || isNaN(lap1) || isNaN(lap2)) return;

  // Carrega os dados de telemetria
  pilotData = await fetchData(`telemetria_volta/${pilot1Index}/${pilot2Index}`);
  const pilot1LapData = pilotData.piloto1.laps[lap1];
  const pilot2LapData = pilotData.piloto2.laps[lap2];

  // Atualiza o mapa
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Desenha o traçado
  ctx.beginPath();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 5;
  for (let i = 0; i < trackPath.length; i++) {
    const [x, z] = normalizeCoordinates(trackPath[i][0], trackPath[i][1], canvas.width, canvas.height);
    if (i === 0) {
      ctx.moveTo(x, z);
    } else {
      ctx.lineTo(x, z);
    }
  }
  ctx.stroke();

  // Desenha os pilotos
  if (pilot1LapData && pilot2LapData && pilot1LapData.lapDistance.length > 0 && pilot2LapData.lapDistance.length > 0) {
    const pilot1Pos = getPositionOnTrack(pilot1LapData.lapDistance[pilot1LapData.lapDistance.length - 1]);
    const pilot2Pos = getPositionOnTrack(pilot2LapData.lapDistance[pilot2LapData.lapDistance.length - 1]);

    ctx.beginPath();
    ctx.fillStyle = '#ff6200'; // Laranja para Piloto 1
    ctx.arc(pilot1Pos[0], pilot1Pos[1], 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = '#fff'; // Branco para Piloto 2
    ctx.arc(pilot2Pos[0], pilot2Pos[1], 8, 0, Math.PI * 2);
    ctx.fill();

    const tempos = await fetchData('tempos');
    const pilot1Time = tempos[pilot1Index].lapTime;
    const pilot2Time = tempos[pilot2Index].lapTime;
    ctx.font = '12px Arial';
    ctx.fillStyle = '#ff6200';
    ctx.fillText(`${pilotData.nomes.piloto1} - Lap ${lap1} - ${formatTime(pilot1Time)}`, pilot1Pos[0] - 60, pilot1Pos[1] - 15);
    ctx.fillStyle = '#fff';
    ctx.fillText(`${pilotData.nomes.piloto2} - Lap ${lap2} - ${formatTime(pilot2Time)}`, pilot2Pos[0] - 60, pilot2Pos[1] - 15);

    // Atualiza os gráficos de telemetria
    updateTelemetryGraphs(pilot1LapData, pilot2LapData);
  }
}

// Função para atualizar os gráficos de telemetria
function updateTelemetryGraphs(pilot1LapData, pilot2LapData) {
  const labels = pilot1LapData.lapDistance.map((_, index) => index);

  // Destruir gráficos existentes
  if (speedChart) speedChart.destroy();
  if (throttleChart) throttleChart.destroy();
  if (brakeChart) brakeChart.destroy();

  // Criar novos gráficos
  speedChart = new Chart(document.getElementById('speedChart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: pilotData.nomes.piloto1,
          data: pilot1LapData.speed,
          borderColor: '#ff6200',
          fill: false
        },
        {
          label: pilotData.nomes.piloto2,
          data: pilot2LapData.speed,
          borderColor: '#fff',
          fill: false
        }
      ]
    },
    options: {
      scales: {
        x: { display: false },
        y: { beginAtZero: true, title: { display: true, text: 'Speed (km/h)', color: '#fff' } }
      },
      plugins: { legend: { labels: { color: '#fff' } } }
    }
  });

  // Gráficos de throttle e brake seguem a mesma lógica
}

// Função para limpar marcadores
function clearMarkers() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  updateMapAndGraphs();
}

async function saveTelemetryData() {
  const pilot1Select = document.getElementById('pilot1');
  const pilot2Select = document.getElementById('pilot2');
  const lap1Select = document.getElementById('lap1');
  const lap2Select = document.getElementById('lap2');
  const pilot1Index = parseInt(pilot1Select.value);
  const pilot2Index = parseInt(pilot2Select.value);
  const lap1 = parseInt(lap1Select.value);
  const lap2 = parseInt(lap2Select.value);

  if (isNaN(pilot1Index) || isNaN(pilot2Index) || isNaN(lap1) || isNaN(lap2)) {
    alert("Selecione pilotos e voltas antes de salvar os dados.");
    return;
  }

  const data = {
    piloto1: {
      nome: pilotData.nomes.piloto1,
      lap: lap1,
      lapData: pilotData.piloto1.laps[lap1]
    },
    piloto2: {
      nome: pilotData.nomes.piloto2,
      lap: lap2,
      lapData: pilotData.piloto2.laps[lap2]
    }
  };

  try {
    const response = await fetch('http://localhost:5000/save-telemetry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    if (result.status === "success") {
      alert("Dados salvos com sucesso!");
    } else {
      alert("Erro ao salvar os dados: " + result.message);
    }
  } catch (error) {
    console.error("Erro ao salvar os dados:", error);
  }
}

async function showSavedTelemetry() {
  const container = document.getElementById('saved-telemetry-list');
  container.innerHTML = "Carregando...";
  try {
    const res = await fetch('http://localhost:5000/api/telemetry-logs');
    const logs = await res.json();
    if (!logs.length) {
      container.innerHTML = "<em>Nenhum dado salvo.</em>";
      return;
    }
    container.innerHTML = logs.map((item, idx) => `
      <div style="margin-bottom:15px; border-bottom:1px solid #444; padding-bottom:10px;">
        <strong>Registro #${idx+1}</strong><br>
        <b>Piloto 1:</b> ${item.piloto1.nome} | <b>Volta:</b> ${item.piloto1.lap}<br>
        <b>Piloto 2:</b> ${item.piloto2.nome} | <b>Volta:</b> ${item.piloto2.lap}<br>
        <details>
          <summary>Ver dados completos</summary>
          <pre style="white-space:pre-wrap; color:#ccc; background:#111; padding:8px; border-radius:4px;">${JSON.stringify(item, null, 2)}</pre>
        </details>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = "Erro ao carregar dados salvos.";
  }
}

// Inicializa a página
updateEventSelector();
