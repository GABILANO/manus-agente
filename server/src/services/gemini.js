_const { GoogleGenAI } = require('@google/genai');
const logger = require('../../utils/logger');

// Inicializar el cliente de Gemini
// La clave de API se toma automáticamente de la variable de entorno GEMINI_API_KEY
const ai = new GoogleGenAI({});

/**
 * Convierte un buffer de imagen a un objeto Part para la API de Gemini.
 * @param {Buffer} buffer - El buffer de la imagen.
 * @param {string} mimeType - El tipo MIME de la imagen (e.g., 'image/jpeg', 'image/png').
 * @returns {Object} Un objeto Part con los datos en línea.
 */
function fileToGenerativePart(buffer, mimeType) {
  return {
    inlineData: {
      data: buffer.toString("base64"),
      mimeType
    },
  };
}

/**
 * Genera contenido de texto o multimodal usando el modelo Gemini.
 * @param {string} prompt - El mensaje de texto del usuario.
 * @param {Array<Object>} [imageParts=[]] - Array de objetos de imagen en formato { inlineData: { data: string, mimeType: string } }.
 * @param {string} [model='gemini-2.5-flash'] - El modelo de Gemini a usar.
 * @returns {Promise<string>} La respuesta de texto del modelo.
 */
async function generateContent(prompt, imageParts = [], model = 'gemini-2.5-flash') {
  const contents = [
    ...imageParts,
    { text: prompt }
  ];

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: [{ role: "user", parts: contents }],
    });

    return response.text;
  } catch (error) {
    logger.error(`Error al generar contenido con Gemini (${model}):`, error);
    // En un entorno real, se podría implementar lógica de reintento o fallback.
    throw new Error('Fallo en la comunicación con la API de Gemini.');
  }
}

// Se mantiene el esqueleto de la función original, pero se adapta a una función de utilidad
// para el futuro manejo de generación de activos, aunque la funcionalidad de Veo se omite.
async function generateAsset(prompt, type = 'image') {
  logger.warn(`La generación de activos de tipo "${type}" no está implementada completamente (Veo API omitida).`);
  // Aquí se podría integrar la generación de imágenes con Imagen o un servicio similar.
  return `Activo generado simulado para: ${prompt} (Tipo: ${type})`;
}

module.exports = {
  generateContent,
  generateAsset,
  fileToGenerativePart,
};_
