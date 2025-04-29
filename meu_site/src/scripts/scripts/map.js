async function fetchCarPositions() {
    const response = await fetch('/api/map_data');
    const data = await response.json();
    updateMap(data);
  }
  
  function updateMap(data) {
    const svg = document.getElementById("car-layer");
  
    for (const piloto in data) {
      let [x, y] = data[piloto];
  
      // Normalizar se necessário: ex, converter do range do jogo para SVG
      // Aqui assumimos que os valores já estão escalados ou cabem na pista
  
      let car = document.getElementById(`car-${piloto}`);
  
      if (!car) {
        car = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        car.setAttribute("id", `car-${piloto}`);
        car.setAttribute("class", "car-dot");
        svg.appendChild(car);
      }
  
      car.setAttribute("cx", x);
      car.setAttribute("cy", y);
    }
  }
  
  setInterval(fetchCarPositions, 100);
  