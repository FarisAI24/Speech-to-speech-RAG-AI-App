import os
import pyaudio
import numpy as np
import whisper
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from elevenlabs import Voice, play
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

client = ElevenLabs(
    api_key=os.getenv('ELEVENLABS_API_KEY'),
)

def record_audio(duration=5, fs=16000, chunk_size=1024):
    """
    Record audio from the microphone.
    :param duration: Length of the recording in seconds (default 5 seconds).
    :param fs: Sampling rate (default 16000 Hz).
    :param chunk_size: Size of each audio chunk (default 1024).
    :return: Numpy array with the recorded audio data.
    """
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=pyaudio.paFloat32,  # 32-bit floating point
                    channels=1,  # Mono
                    rate=fs,  # Sampling rate
                    input=True,
                    frames_per_buffer=chunk_size)

    print("Recording...")
    frames = []
    for _ in range(0, int(fs / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(np.frombuffer(data, dtype=np.float32))  # Convert buffer to numpy array

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Recording finished.")
    return np.concatenate(frames)

def transcribe_audio(audio_data):
    """
    Transcribe audio using the Whisper model.
    :param audio_data: Numpy array containing audio data.
    """
    model = whisper.load_model("small") # Whisper offers different models, "small" is a lightweight model.
    result = model.transcribe(audio_data)
    return result["text"]

def text_to_speech(text):
    """
    Convert text to speech using the ElevenTTS API.
    :param text: Text to convert to speech.
    """
    audio = client.generate(
        text = text,
        voice = Voice(
            voice_id = os.getenv('ELEVENLABS_VOICE_ID'),
        ),
    )
    play(audio)

def Settings():
    """
    Setting up the settings needed for the both the LLM and embedding models
    :param: None
    :return: None
    """
    # Embedding model
    embedding_model = OpenAIEmbedding(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-3-small",
    )

    Settings.llm = Ollama(model="llama3", request_timeout=30.0)
    Settings.embed_model = embedding_model

def llm_usage(text):
    """
    Setting up the vector store for the query engine and query the database
    :param None
    :return: reponse
    """
    # VectorStore
    qdrant_client = QdrantClient(url=os.getenv('QDRANT_API_URL'), api_key=os.getenv('QDRANT_API_KEY'))
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name="testing")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Indexing the vector store
    index = VectorStoreIndex.from_documents(
    [],
    storage_context=storage_context,
    )
    # initialize the index as a query engine to query the database.
    query_engine = index.as_query_engine()
    # Query the query engine.
    query = query_engine.query(text)
    # returns the response.
    return query.response

def main():
    Settings()
    audio = record_audio() # Record 4 seconds of audio
    text = transcribe_audio(audio) # Transcribe the audio
    print(f"User: {text}") # Print Transcribed Audio
    response = llm_usage(text) # Query the LLM model
    print(f"AIChatbot: {response}") # Print Response
    text_to_speech(response) # Convert the response to speech

if __name__ == "__main__":
    main()