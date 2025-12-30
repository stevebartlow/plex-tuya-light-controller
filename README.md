# Plex -> Feit/Tuya Lighting Controller

This project automatically syncs your Feit Electric (or any Tuya-compatible) smart lights to the dominant color of the movie poster playing on your Plex Media Server.

## Features
*   **Automatic Color Sync**: Changes light colors based on the playing media's poster.
*   **Player Filtering**: Only triggers for specific devices (e.g., "Living Room TV").
*   **Dockerized**: Easy to deploy on your home server.
*   **Local Control**: Uses `tinytuya` for local LAN control (fast & private), though setup requires fetching keys once from the cloud.

## Prerequisites
1.  **Plex Media Server** (with Plex Pass for Webhooks).
2.  **Feit Electric / Tuya Smart Lights**.
3.  **Tuya Developer Account** (free) to get Local Keys.
4.  **Docker**.

## Setup Guide

### 1. Get Tuya Local Keys
You need the `local_key` for your lights. The easiest way is to use the `tinytuya` wizard on your local machine (mac/linux):
```bash
# Install tinytuya locally just for the wizard
pip install tinytuya
python3 -m tinytuya wizard
```
Follow the prompts. This will generate a `devices.json` file.
**Move this `devices.json` file into this project folder.**

*Alternatively, create `devices.json` manually:*
```json
[
  {
    "name": "My Light",
    "id": "YOUR_DEVICE_ID",
    "ip": "192.168.1.XXX",
    "key": "YOUR_LOCAL_KEY",
    "version": 3.3
  }
]
```
> **Important**: You MUST include the `ip` address for Docker execution, as auto-discovery does not work across the container boundary.

### 2. Configure Application
Edit `config.py` with your settings:
*   `PLEX_TOKEN`: Your X-Plex-Token (Find this in Plex Web -> Media Info -> View XML).
*   `PLEX_URL`: URL of your Plex server (e.g., `http://192.168.1.10:32400` or `http://plex:32400` if in same docker network).
*   `TARGET_PLAYER_NAME`: (Optional) The name of the Plex client to react to (e.g. `Roku Ultra`). Leave empty to react to all.

### 3. Run with Docker
```bash
docker compose up -d --build
```
This maps port `5001` to your host.

### 4. Configure Plex Webhook
1.  Open Plex Web App.
2.  Go to **Settings** > **Webhooks**.
3.  Click **Add Webhook**.
4.  URL: `http://<YOUR_SERVER_IP>:5001/webhook`

## Troubleshooting
*   **"Bulb not configured" / Connection Failed**: Ensure the IP address in `devices.json` is correct and static. The container cannot scan for devices; it needs explicit IPs.
*   **404 Error**: Make sure your webhook URL ends in `/webhook`.
*   **Wrong Colors**: The script takes the deeper dominant color. Dark posters might result in dim lights.
