import os
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/get-youtube', methods=['POST', 'GET'])
def get_youtube():
    data = request.get_json(silent=True) or {}
    url = data.get('url') if request.method == 'POST' else request.args.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'No YouTube URL provided'}), 400

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'YouTube Media')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            uploader = info.get('uploader', 'YouTube Channel')
            
            formats_list = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Combined formats
                    formats_list.append({
                        'quality': f.get('format_note') or f.get('resolution') or 'HD',
                        'ext': f.get('ext', 'mp4'),
                        'url': f.get('url'),
                        'filesize': f.get('filesize') or f.get('filesize_approx') or 0
                    })

            # Fallback if no combined format found
            if not formats_list and info.get('url'):
                formats_list.append({
                    'quality': 'HD 1080p',
                    'ext': info.get('ext', 'mp4'),
                    'url': info.get('url'),
                    'filesize': 0
                })

            return jsonify({
                'success': True,
                'title': title,
                'uploader': uploader,
                'duration': duration,
                'thumbnail': thumbnail,
                'mediaList': formats_list
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'YouTube Downloader API is running on Vercel!'})

if __name__ == '__main__':
    app.run(debug=True)
