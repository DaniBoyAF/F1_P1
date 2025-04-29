async function main() {
    const res = await fetch("corrida_miami_2024-05-05.json");
    const data = await res.json();

    const pilotos = Object.keys(data.pilotos);
    const tempos = Object.values(data.pilotos);

    document.getElementById("titulo").innerText = `📍 Corrida em ${data.pista}`;

    // -------- BOXPLOT --------
    const boxData = pilotos.map((piloto, i) => ({
      label: piloto,
      data: [tempos[i]],
      backgroundColor: `hsl(${(i * 30) % 360}, 70%, 60%)`
    }));

    new Chart(document.getElementById("boxplot"), {
      type: "boxplot",
      data: {
        labels: pilotos,
        datasets: boxData
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Distribuição dos Tempos por Piloto (Boxplot)"
          }
        }
      }
    });

    // -------- LINHAS --------
    const voltas = tempos[0].length;
    const labels = Array.from({ length: voltas }, (_, i) => i + 1);

    const lineData = pilotos.map((piloto, i) => ({
      label: piloto,
      data: tempos[i],
      borderColor: `hsl(${(i * 30) % 360}, 70%, 50%)`,
      borderWidth: 1.5,
      tension: 0.3,
      fill: false
    }));

    new Chart(document.getElementById("linhas"), {
      type: "line",
      data: {
        labels: labels,
        datasets: lineData
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Tempos por Volta - Todos os Pilotos"
          }
        },
        scales: {
          y: {
            title: {
              display: true,
              text: "Tempo (s)"
            }
          },
          x: {
            title: {
              display: true,
              text: "Volta"
            }
          }
        }
      }
    });
  }

  main();