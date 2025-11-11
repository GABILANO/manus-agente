_const express = require('express');
const router = express.Router();
const { getAuthUrl, handleCallback } = require('../auth/google');
const logger = require('../../utils/logger');

/**
 * GET /auth/google
 * Redirige al usuario a la página de consentimiento de Google.
 */
router.get('/google', (req, res) => {
  const authUrl = getAuthUrl();
  res.redirect(authUrl);
});

/**
 * GET /auth/google/callback
 * Maneja la respuesta de Google, obtiene tokens y redirige al frontend.
 */
router.get('/google/callback', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    logger.error('Callback de Google sin código de autorización.');
    return res.status(400).send('Error de autenticación: Código no proporcionado.');
  }

  try {
    const { access_token, refresh_token_encrypted } = await handleCallback(code);

    // NOTA: En un entorno real, aquí se establecería una cookie de sesión o se devolvería
    // un token JWT al frontend para que lo almacene.
    // También se guardaría el refresh_token_encrypted de forma segura (e.g., en GitHub Secrets).

    logger.info('Autenticación exitosa. Refresh token cifrado generado.');

    // Redirigir al frontend con información de éxito (o un token JWT)
    // Se asume que el frontend está en la raíz para este ejemplo.
    res.redirect(`/?auth_success=true&access_token=${access_token.substring(0, 10)}...`);

  } catch (error) {
    logger.error('Fallo en el callback de Google:', error);
    res.status(500).send(`Error de autenticación: ${error.message}`);
  }
});

module.exports = router;_
