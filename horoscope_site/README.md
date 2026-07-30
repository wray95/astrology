# Gochara Atlas — Horoscope Attachment Chat

A GitHub Pages-friendly static frontend plus a separate secure Node backend for OpenAI-powered PDF/image horoscope chat.

## Security

Never put the OpenAI API key in `index.html`, `app.js` or GitHub Pages. The key belongs only in `server/.env`, which must not be committed. The browser calls the backend; the backend calls OpenAI.

## Run locally

```bash
cd horoscope_site/server
cp .env.example .env
# edit .env and add OPENAI_API_KEY
npm install
npm run dev
```

In another terminal, serve the frontend:

```bash
cd horoscope_site
python3 -m http.server 8080
```

Open `http://localhost:8080`. The frontend defaults to `http://localhost:8787`; for production set `window.HOROSCOPE_API_BASE` to your deployed backend URL before `app.js` loads.

## Deploy

- Publish `horoscope_site/` as the GitHub Pages artifact.
- Deploy `horoscope_site/server/` to a serverless/container host such as Render, Railway, Fly.io, Cloud Run or a Node-capable function platform.
- Set `OPENAI_API_KEY`, `OPENAI_MODEL` and `ALLOWED_ORIGIN` in the backend platform secrets.
- Restrict CORS to the GitHub Pages origin in production.

## Features

- PDF and PNG/JPEG/WebP attachment upload
- Chat-based source extraction and research questions
- Evidence-first system prompt
- Existing matrix/Shrinkala dashboard links
- Q/P dataset summary cards
- No birth-time, house or causation claims by default
