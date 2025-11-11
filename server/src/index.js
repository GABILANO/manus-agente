_const express = require('express');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const Redis = require('ioredis');
const logger = require('../utils/logger');
const apiRoutes = require('./routes/api');
// const authRoutes = require('./routes/auth'); // Se implementará en una fase posterior

// Cargar variables de entorno
dotenv.config({ path: '../../.env' });

const app = express();
const PORT = process.env.PORT || 3000;

// Conexión a Redis (opcional, para colas o caché)
try {
  const redis = new Redis(process.env.REDIS_URL);
  redis.on('connect', () => logger.info('Conectado a Redis'));
  redis.on('error', (err) => logger.error('No se pudo conectar a Redis:', err));
  app.set('redis', redis);
} catch (error) {
  logger.warn('Redis no está configurado. El worker y la caché no estarán disponibles.');
}

// Middleware
app.use(bodyParser.json());

// Rutas
app.use('/api', apiRoutes);
// app.use('/auth', authRoutes);

app.get('/', (req, res) => {
  res.status(200).send('Servidor de manus-agente está en funcionamiento.');
});

// Middleware de manejo de errores
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).json({ error: 'Ocurrió un error interno en el servidor.' });
});

app.listen(PORT, () => {
  logger.info(`Servidor escuchando en http://localhost:${PORT} en modo ${process.env.NODE_ENV}`);
});_
