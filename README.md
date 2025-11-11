# 🤖 manus-agente

**manus-agente** es un agente de IA full-stack inspirado en el concepto de un agente autónomo, implementado con un backend seguro en **Node.js/Express** y un frontend moderno en **SvelteKit**. Prioriza la seguridad, la ejecución nativa en GitHub (Codespaces/Actions) y la integración con la **API oficial de Google Gemini**.

## 🚀 Visión General

El objetivo de este proyecto es proporcionar un esqueleto de agente de IA robusto y seguro, centrado en:
1.  **Integración Segura con Google**: Uso de OAuth2 para autenticación y acceso a servicios de Google (Gemini, etc.).
2.  **Seguridad Crítica**: Implementación de cifrado AES-256 para tokens sensibles y un esqueleto para la rotación automática de tokens.
3.  **Arquitectura Escalable**: Separación clara entre el servidor (API) y el cliente (UI), con soporte para colas de trabajo asíncronas (Redis).

## 🛠️ Instalación en 3 Pasos

Este proyecto está diseñado para ser desplegado y ejecutado fácilmente en **GitHub Codespaces** o en su entorno local.

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/manus-agente.git
cd manus-agente
```

### Paso 2: Configuración de Variables de Entorno

1.  **Crea un archivo `.env`** en la raíz del proyecto, copiando el contenido de `.env.example`.
    ```bash
    cp .env.example .env
    ```
2.  **Configura `SERVER_SECRET`**: Genera una clave secreta larga y aleatoria (mínimo 32 caracteres) para el cifrado de tokens.
3.  **Configura Google OAuth2**:
    *   Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/).
    *   Habilita la **API de Google People** y la **API de Gemini**.
    *   Crea credenciales de **ID de cliente de OAuth 2.0** para una **Aplicación web**.
    *   Añade `http://localhost:3000/auth/google/callback` como URI de redirección autorizado (ajusta el puerto si es necesario).
    *   Rellena `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `GOOGLE_REDIRECT_URI` en tu archivo `.env`.
4.  **Configura Gemini API**: Obtén tu clave de API de Gemini y rellena `GEMINI_API_KEY`.

### Paso 3: Ejecutar el Proyecto

El proyecto utiliza Docker Compose para levantar el servidor y Redis.

```bash
# Construir y levantar los contenedores
docker-compose -f infra/docker-compose.yml up --build
```

El servidor estará disponible en `http://localhost:3000` y el frontend en `http://localhost:5173` (si se ejecuta por separado).

## 🔒 Seguridad Crítica (Implementación Esqueleto)

El proyecto incluye mecanismos de seguridad esenciales:

### Cifrado de Tokens (AES-256)

El `refresh_token` de Google se cifra con **AES-256-CBC** antes de ser almacenado. La clave de cifrado se deriva de la variable de entorno `SERVER_SECRET`.

### Rotación de Tokens (Esqueleto)

El archivo `.github/workflows/refresh-token-action.yml` (que crearemos en la siguiente fase) contendrá el esqueleto para un flujo de trabajo de GitHub Actions que podría ser configurado para:
1.  Descifrar el `refresh_token` almacenado en un GitHub Secret.
2.  Usar la función `refreshAccessToken` en `server/src/auth/google.js` para obtener un nuevo par de tokens.
3.  Cifrar el nuevo `refresh_token`.
4.  Actualizar el GitHub Secret con el nuevo token cifrado.

### Revocación de Tokens

Se recomienda encarecidamente que, en caso de una brecha de seguridad, se revoque inmediatamente el acceso a la aplicación desde la configuración de su cuenta de Google.

## 💡 Ejemplos de Prompts (Demo)

El archivo `examples/demo-prompts.md` contiene ejemplos de prompts para probar la funcionalidad de **análisis multimodal** y **generación de texto** con Gemini.

> **Nota Estratégica:** La funcionalidad de generación de videos con la supuesta "Veo API" y el bypass de filtros de seguridad ha sido **omitida** de esta implementación por razones de viabilidad técnica (la API no es pública) y por adherencia a las políticas de uso ético y seguro de la IA. El proyecto se centra en la integración segura y funcional con la API oficial de Gemini.
