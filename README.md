---
title: Quantview Backend
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
docker:
  dockerfile: backend/Dockerfile
---

# QuantView Monorepo

This repository contains:
- `/frontend`: Next.js frontend
- `/backend`: FastAPI Python backend (deployed to Hugging Face Space using the custom Dockerfile configuration).
