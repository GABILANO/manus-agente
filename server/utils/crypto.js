_const crypto = require('crypto');
const logger = require('./logger');

const ALGORITHM = 'aes-256-cbc';
const IV_LENGTH = 16; // Para AES-256-CBC

/**
 * Obtiene la clave de cifrado del entorno.
 * @returns {Buffer} La clave de cifrado.
 * @throws {Error} Si SERVER_SECRET no está definido o no tiene la longitud correcta.
 */
function getEncryptionKey() {
  const secret = process.env.SERVER_SECRET;
  if (!secret || secret.length < 32) {
    logger.error('SERVER_SECRET no está configurado o es demasiado corto. Se requiere una clave de al menos 32 bytes.');
    throw new Error('SERVER_SECRET no configurado correctamente.');
  }
  // Usar SHA-256 para asegurar que la clave tenga 32 bytes (256 bits)
  return crypto.createHash('sha256').update(secret).digest();
}

/**
 * Cifra un texto usando AES-256-CBC.
 * @param {string} text - El texto a cifrar.
 * @returns {string} El texto cifrado en formato 'iv:encryptedText'.
 */
function encrypt(text) {
  try {
    const key = getEncryptionKey();
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
  } catch (error) {
    logger.error('Error al cifrar:', error);
    throw new Error('Fallo en el proceso de cifrado.');
  }
}

/**
 * Descifra un texto cifrado con AES-256-CBC.
 * @param {string} text - El texto cifrado en formato 'iv:encryptedText'.
 * @returns {string} El texto descifrado.
 */
function decrypt(text) {
  try {
    const key = getEncryptionKey();
    const parts = text.split(':');
    if (parts.length !== 2) {
      throw new Error('Formato de texto cifrado inválido.');
    }
    const iv = Buffer.from(parts[0], 'hex');
    const encryptedText = parts[1];
    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  } catch (error) {
    logger.error('Error al descifrar:', error);
    throw new Error('Fallo en el proceso de descifrado.');
  }
}

module.exports = {
  encrypt,
  decrypt,
};_
