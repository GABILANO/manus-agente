_const { OAuth2Client } = require('google-auth-library');
const { encrypt, decrypt } = require('../../utils/crypto');
const logger = require('../../utils/logger');

// Inicializar el cliente OAuth2
const oauth2Client = new OAuth2Client(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

// Scopes mínimos requeridos (ajustar según necesidad real)
const SCOPES = [
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile',
  // Se omite cualquier scope relacionado con Veo o APIs no existentes
];

/**
 * Genera la URL de autenticación de Google.
 * @returns {string} La URL de autenticación.
 */
function getAuthUrl() {
  return oauth2Client.generateAuthUrl({
    access_type: 'offline', // Importante para obtener el refresh_token
    scope: SCOPES,
    prompt: 'consent', // Forzar el consentimiento para obtener siempre el refresh_token
  });
}

/**
 * Maneja el callback de OAuth2, obtiene tokens y cifra el refresh_token.
 * @param {string} code - El código de autorización de Google.
 * @returns {Promise<{access_token: string, refresh_token_encrypted: string}>} Los tokens.
 */
async function handleCallback(code) {
  try {
    const { tokens } = await oauth2Client.getToken(code);

    if (!tokens.refresh_token) {
      logger.warn('No se recibió refresh_token. Asegúrese de que access_type sea "offline" y prompt sea "consent".');
      // En un entorno real, se podría forzar al usuario a reautenticar.
    }

    const encryptedRefreshToken = tokens.refresh_token ? encrypt(tokens.refresh_token) : null;

    // NOTA: En la implementación final, 'saveToSecrets' debe ser una función que interactúe
    // con el sistema de secretos de GitHub Actions o una base de datos segura.
    // Aquí, solo devolvemos el token cifrado.
    // await saveToSecrets("GOOGLE_REFRESH_TOKEN", encryptedRefreshToken);

    return {
      access_token: tokens.access_token,
      refresh_token_encrypted: encryptedRefreshToken
    };
  } catch (error) {
    logger.error('Error al manejar el callback de Google OAuth2:', error);
    throw new Error('Fallo en la autenticación con Google.');
  }
}

/**
 * Usa el refresh_token cifrado para obtener un nuevo access_token.
 * @param {string} encryptedRefreshToken - El refresh_token cifrado.
 * @returns {Promise<string>} El nuevo access_token.
 */
async function refreshAccessToken(encryptedRefreshToken) {
  try {
    const refreshToken = decrypt(encryptedRefreshToken);
    oauth2Client.setCredentials({ refresh_token: refreshToken });
    const { credentials } = await oauth2Client.refreshAccessToken();
    return credentials.access_token;
  } catch (error) {
    logger.error('Error al refrescar el access_token:', error);
    throw new Error('Fallo al refrescar el token. Se requiere reautenticación.');
  }
}

module.exports = {
  getAuthUrl,
  handleCallback,
  refreshAccessToken,
  oauth2Client,
};_
