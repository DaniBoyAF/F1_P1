fetch("/static/velocidades.json")
  .then(res => res.json())
  .then(drivers => {
    const chart = document.getElementById('chart');
    const speeds = Object.values(drivers);
    const maxSpeed = Math.max(...speeds.map(d => d.speed));

    for (const [name, data] of Object.entries(drivers)) {
      const barContainer = document.createElement('div');
      barContainer.className = 'bar-container';

      const bar = document.createElement('div');
      bar.className = 'bar';
      const height = (data.speed / maxSpeed) * 300;
      bar.style.height = `${height}px`;
      bar.style.backgroundColor = data.team || "#007bff"; // cor do time
      bar.textContent = data.speed;

      const label = document.createElement('div');
      label.className = 'label';
      label.innerHTML = `${name}<br>${data.tyre}`;

      barContainer.appendChild(bar);
      barContainer.appendChild(label);
      chart.appendChild(barContainer);
    }
  });