document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('.login-form');

    form.addEventListener('submit', function(event) {
      event.preventDefault(); // impede o formulário de recarregar a página

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      console.log("Tentando logar com:");
      console.log("Email:", email);
      console.log("Senha:", password);

      // Aqui você faria a chamada para autenticar (exemplo)
      if (email === "teste@email.com" && password === "123456") {
        alert("Login realizado com sucesso!");
        // redirecionar para outra página
        window.location.href = "/dashboard.html"; 
      } else {
        alert("Email ou senha incorretos.");
      }
    });
  });

