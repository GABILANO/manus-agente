_const express = require('express');
const router = express.Router();
const { generateContent, fileToGenerativePart } = require('../services/gemini');
const { generateShortVideo } = require('../services/veo'); // Se mantiene la importación para la estructura
const logger = require('../../utils/logger');

// Middleware de autenticación simulado (se implementará correctamente en la fase 3)
const authenticate = (req, res, next) => {
  // En un entorno real, se verificaría un token JWT o una sesión.
  // Por ahora, solo simula que el usuario está autenticado.
  req.user = { id: 'user-123', name: 'Authenticated User' };
  next();
};

/**
 * POST /api/agent/message
 * Recibe texto e imágenes, usa Gemini para análisis multimodal y responde.
 */
router.post('/agent/message', authenticate, async (req, res) => {
  const { prompt, images } = req.body; // 'images' debe ser un array de objetos { data: string (base64), mimeType: string }

  if (!prompt) {
    return res.status(400).json({ error: 'El campo "prompt" es obligatorio.' });
  }

  try {
    let imageParts = [];
    if (images && images.length > 0) {
      // Convertir las imágenes de base64 a partes de Gemini
      imageParts = images.map(img => fileToGenerativePart(Buffer.from(img.data, 'base64'), img.mimeType));
    }

    // 1. Respuesta rápida (Gemini Flash)
    const response = await generateContent(prompt, imageParts, 'gemini-2.5-flash');

    // 2. Mejora profunda (procesamiento en segundo plano) - Encolar trabajo
    const redis = req.app.get('redis');
    if (redis) {
      const jobData = { userId: req.user.id, prompt, initialResponse: response };
      // Encolar trabajo para el worker (se implementará en worker.js)
      await redis.lpush('deep_process_queue', JSON.stringify(jobData));
      logger.info(`Trabajo de mejora profunda encolado para el usuario ${req.user.id}.`);
    }

    res.json({
      status: 'success',
      response: response,
      deep_processing: !!redis,
      message: 'Respuesta rápida generada. La mejora profunda está en curso (si Redis está disponible).'
    });

  } catch (error) {
    logger.error('Error en /api/agent/message:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/assets/generate
 * Genera un activo (simulado) y lo encola para procesamiento.
 */
router.post('/assets/generate', authenticate, async (req, res) => {
  const { prompt, type = 'image' } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'El campo "prompt" es obligatorio.' });
  }

  try {
    // Encolar trabajo para el worker (simulando la generación de video/activo)
    const redis = req.app.get('redis');
    if (redis) {
      const jobData = { userId: req.user.id, prompt, type, assetId: Date.now() };
      await redis.lpush('asset_generation_queue', JSON.stringify(jobData));
      logger.info(`Trabajo de generación de activo encolado para el usuario ${req.user.id}.`);
      res.json({
        status: 'queued',
        message: `Generación de activo de tipo ${type} encolada.`,
        jobId: jobData.assetId
      });
    } else {
      // Si Redis no está disponible, se usa la función placeholder de veo.js
      const result = await generateShortVideo(prompt, '16:9');
      res.json({
        status: 'simulated',
        message: 'Generación de activo simulada (Redis no disponible).',
        result: result
      });
    }
  } catch (error) {
    logger.error('Error en /api/assets/generate:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;_
