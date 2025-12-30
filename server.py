from flask import Flask, request, jsonify
import json
import logging
import requests
from config import PLEX_TOKEN, PLEX_URL
from utils import get_dominant_color_from_bytes
from light_control import LightController

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Light Controller
light_controller = LightController()

@app.route('/webhook', methods=['POST'])
def webhook():
    # Plex sends a multipart request. The 'payload' field contains the JSON.
    if 'payload' not in request.form:
        return jsonify({'error': 'No payload found'}), 400

    payload_json = request.form['payload']
    try:
        data = json.loads(payload_json)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400

    event = data.get('event')
    logger.info(f"Received event: {event}")

    # Inspect Metadata for Poster
    metadata = data.get('Metadata', {})
    player = data.get('Player', {})

    player_name = player.get('title', '')
    logger.info(f"Player name: {player_name}")

    # Filter by Player Name if configured
    from config import TARGET_PLAYER_NAME
    if TARGET_PLAYER_NAME:
        player_name = player.get('title', '')
        # Check if the player name contains the target (case-insensitive)
        if TARGET_PLAYER_NAME.lower() not in player_name.lower():
            logger.info(f"Ignoring event from player '{player_name}' (Target: '{TARGET_PLAYER_NAME}')")
            return jsonify({'status': 'ignored', 'reason': 'player_mismatch'}), 200
    
    # Logic: 
    # media.play / media.resume -> Extract color & Set Light
    # media.pause / media.stop -> Reset Light (Optional, maybe just stop is enough)
    
    if event in ['media.play', 'media.resume']:
        thumb_url = metadata.get('thumb')
        if thumb_url:
            # Construct full URL. 
            # Plex local URLs are like: /library/metadata/123/thumb/123456...
            # We need to prepend the server URL and append the Token
            full_image_url = f"{PLEX_URL}{thumb_url}?X-Plex-Token={PLEX_TOKEN}"
            logger.info(f"Fetching poster from: {full_image_url}")
            
            try:
                # Fetch image directly here to pass bytes to utils
                r = requests.get(full_image_url)
                if r.status_code == 200:
                    dominant_color = get_dominant_color_from_bytes(r.content)
                    if dominant_color:
                        r_val, g_val, b_val = dominant_color
                        light_controller.set_color(r_val, g_val, b_val)
                    else:
                        logger.warning("Could not extract color from image")
                else:
                    logger.error(f"Failed to fetch image. Status: {r.status_code}")

            except Exception as e:
                logger.error(f"Error processing image: {e}")
        else:
            logger.info("No thumb image found in metadata")

    elif event in ['media.stop', 'media.pause']:
        logger.info("Media stopped/paused. Resetting lights.")
        light_controller.set_white()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible on local network
    app.run(host='0.0.0.0', port=5001, debug=True)
