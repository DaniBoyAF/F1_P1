// settings.js
// Função para carregar as configurações do servidor e preencher o formulário
    async function loadSettings() {
      try {
        const response = await fetch('http://localhost:5000/api/settings');
        const settings = await response.json();
        document.getElementById('updateInterval').value = settings.updateInterval;
        document.getElementById('theme').value = settings.theme;
        document.getElementById('udpPort').value = settings.udpPort;
        document.getElementById('language').value = settings.language;
      } catch (error) {
        console.error('Erro ao carregar configurações:', error);
      }
    }
    
    // Salva as configurações ao enviar o formulário
    document.getElementById('settingsForm').addEventListener('submit', async (event) => {
      event.preventDefault();
      const settings = {
        updateInterval: parseInt(document.getElementById('updateInterval').value),
        theme: document.getElementById('theme').value,
        udpPort: parseInt(document.getElementById('udpPort').value),
        language: document.getElementById('language').value
      };
    
      try {
        const response = await fetch('http://localhost:5000/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(settings)
        });
        const result = await response.json();
        if (result.status === 'success') {
          document.getElementById('statusMessage').textContent = 'Settings saved successfully!';
          document.getElementById('statusMessage').style.color = '#0f0';
        } else {
          throw new Error('Failed to save settings');
        }
      } catch (error) {
        console.error('Erro ao salvar configurações:', error);
        document.getElementById('statusMessage').textContent = 'Error saving settings.';
        document.getElementById('statusMessage').style.color = '#f00';
      }});
    
    // Carrega as configurações ao carregar a página
    loadSettings();