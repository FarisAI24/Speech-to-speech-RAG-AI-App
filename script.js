document.addEventListener('DOMContentLoaded', function() {
    var soundWave = document.querySelector('.sound-wave');
    if (!soundWave) {
        console.error('No sound wave element found!');
        return;
    }
    soundWave.classList.add('stopped');
});

document.addEventListener('keydown', function(event) {
    if (event.code === 'Space') {
        event.preventDefault();
        var soundWave = document.querySelector('.sound-wave');
        if (!soundWave) {
            console.error('No sound wave element found!');
            return;
        }
        if (soundWave.classList.contains('stopped')) {
            soundWave.classList.remove('stopped');
            let bars = soundWave.querySelectorAll('.bar');
            if (!bars.length) {
                console.error('No bars found in sound wave!');
                return;
            }
            bars.forEach(bar => {
                bar.style.animation = '';
            });
            startRecording();
        } else {
            soundWave.classList.add('stopped');
            let bars = soundWave.querySelectorAll('.bar');
            if (!bars.length) {
                console.error('No bars found in sound wave!');
                return;
            }
            bars.forEach(bar => {
                var currentHeight = getComputedStyle(bar).height;
                bar.style.animation = 'none';
                setTimeout(() => {
                    bar.style.height = currentHeight;
                    bar.style.animation = `reduceHeightFromCurrent 0.8s forwards`;
                }, 10);
            });
        }
    }
});

function startRecording() {
    fetch('http://127.0.0.1:5000/record_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ duration: 5 }) // Example: recording for 5 seconds
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Recording successful", data);
        transcribeAudio(data.data);
    })
    .catch(error => console.error('Error:', error));
}

function transcribeAudio(audioData) {
    fetch('http://127.0.0.1:5000/transcribe_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ audio_data: audioData })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Transcription: ", data.transcribed_text);
        respond(data.transcribed_text);
        displayTextWordByWord(data.transcribed_text, 'inputText', 100);
    })
    .catch(error => console.error('Error:', error));
}

function respond(transcribedText) {
    fetch('http://127.0.0.1:5000/respond', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: transcribedText })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response: ", data.response);
        textToSpeech(data.response);
        displayTextWordByWord(data.response, 'outputText', 100);
    })
    .catch(error => console.error('Error:', error));
}

function textToSpeech(responseText) {
    fetch('http://127.0.0.1:5000/text_to_speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: responseText })
    })
    .then(() => console.log("Speech played"))
    .catch(error => console.error('Error:', error));
}

function displayTextWordByWord(text, elementId, delay = 100) {
    const words = text.split(' ');
    let index = 0;
    const textBox = document.getElementById(elementId);
    textBox.textContent = ''; 
  
    const intervalId = setInterval(() => {
      if (index < words.length) {
        textBox.textContent += words[index] + ' ';
        index++;
      } else {
        clearInterval(intervalId);
      }
    }, delay);
  }

function toggleMode() {
    var element = document.body;
    var icon = document.querySelector('.toggle-icon');
    element.classList.toggle("dark-mode");
  
    if (element.classList.contains("dark-mode")) {
      icon.classList.remove("fa-moon");
      icon.classList.add("fa-sun");
    } else {
      icon.classList.remove("fa-sun");
      icon.classList.add("fa-moon");
    }
}
