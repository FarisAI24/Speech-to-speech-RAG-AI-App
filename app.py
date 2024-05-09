from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from main import record_audio as main_record_audio, transcribe_audio as main_transcribe_audio, llm_usage, text_to_speech as main_text_to_speech

app = Flask(__name__)
CORS(app)

@app.route('/record_audio', methods=['POST'])
def handle_record_audio():
    duration = request.json.get('duration', 5)
    audio_data = main_record_audio(duration=duration)
    return jsonify({"message": "Recording successful", "data": audio_data.tolist()})

@app.route('/transcribe_audio', methods=['POST'])
def handle_transcribe_audio():
    audio_data = request.json['audio_data']
    text = main_transcribe_audio(np.array(audio_data, dtype=np.float32))
    return jsonify({"transcribed_text": text})

@app.route('/respond', methods=['POST'])
def handle_respond():
    text = request.json['text']
    response = llm_usage(text)
    return jsonify({"response": response})

@app.route('/text_to_speech', methods=['POST'])
def handle_text_to_speech():
    text = request.json['text']
    main_text_to_speech(text)
    return jsonify({"message": "Speech has been played"})

if __name__ == '__main__':
    app.run(debug=True)
