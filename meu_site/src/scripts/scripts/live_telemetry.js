
    // Conecta ao WebSocket
    const socket = io('http://localhost:5000');

    // Atualiza os dados na página quando receber uma mensagem do WebSocket
    socket.on('telemetry_update', (data) => {
      document.getElementById('speed').textContent = data.speed || 0;
      document.getElementById('throttle').textContent = data.throttle ? data.throttle.toFixed(2) : 0;
      document.getElementById('brake').textContent = data.brake ? data.brake.toFixed(2) : 0;
      document.getElementById('gear').textContent = data.gear || 0;
      document.getElementById('rpm').textContent = data.engine_rpm || 0;
      document.getElementById('position').textContent = `${data.position_x ? data.position_x.toFixed(2) : 0}, ${data.position_y ? data.position_y.toFixed(2) : 0}, ${data.position_z ? data.position_z.toFixed(2) : 0}`;
    });
