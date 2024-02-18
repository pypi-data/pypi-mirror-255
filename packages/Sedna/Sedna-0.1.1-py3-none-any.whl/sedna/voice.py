def speak(sentence):

    """
    Speaks the input given
    """

    import pyttsx3

    engine = pyttsx3.init()

    engine.say(sentence)
    engine.runAndWait()
    engine.stop()