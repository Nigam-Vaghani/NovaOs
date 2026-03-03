import speech_recognition as sr


def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣 Recognized: {text}")
        return text

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None

    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return None