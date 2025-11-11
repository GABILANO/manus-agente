_<script>
  import { onMount } from 'svelte';

  let message = '';
  let response = '¡Hola! Soy manus-agente. ¿En qué puedo ayudarte hoy?';
  let isLoading = false;
  let authStatus = 'No autenticado';

  onMount(() => {
    // Verificar si la URL contiene parámetros de autenticación
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_success') === 'true') {
      authStatus = 'Autenticado con éxito';
      // Limpiar la URL
      window.history.replaceState({}, document.title, "/");
    }
  });

  async function sendMessage() {
    if (!message.trim() || isLoading) return;

    isLoading = true;
    const userMessage = message;
    message = '';
    response = 'Pensando...';

    try {
      const res = await fetch('/api/agent/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // En un entorno real, se enviaría un token de autorización
        },
        body: JSON.stringify({ prompt: userMessage })
      });

      const data = await res.json();

      if (res.ok) {
        response = data.response;
      } else {
        response = `Error: ${data.error || 'Fallo al comunicarse con el servidor.'}`;
      }
    } catch (error) {
      response = `Error de red: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  function login() {
    window.location.href = '/auth/google';
  }
</script>

<svelte:head>
  <title>manus-agente - Chat</title>
</svelte:head>

<div class="chat-container">
  <header>
    <h1>manus-agente</h1>
    <p>Estado de autenticación: {authStatus}</p>
    <button on:click={login}>
      {authStatus === 'Autenticado con éxito' ? 'Reautentizar' : 'Iniciar Sesión con Google'}
    </button>
  </header>

  <div class="messages">
    <div class="message agent">
      <p>{response}</p>
    </div>
  </div>

  <form on:submit|preventDefault={sendMessage} class="input-area">
    <input
      type="text"
      bind:value={message}
      placeholder="Escribe tu mensaje..."
      disabled={isLoading}
    />
    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Enviando...' : 'Enviar'}
    </button>
  </form>
</div>

<style>
  /* Estilos básicos móvil-first */
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 600px;
    margin: 0 auto;
    padding: 10px;
    font-family: sans-serif;
  }
  header {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
    text-align: center;
  }
  .messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px 0;
  }
  .message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
  }
  .agent {
    background-color: #f0f0f0;
    align-self: flex-start;
  }
  .input-area {
    display: flex;
    padding: 10px 0;
    border-top: 1px solid #eee;
  }
  .input-area input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-right: 10px;
  }
  .input-area button {
    padding: 10px 15px;
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
</style>_
