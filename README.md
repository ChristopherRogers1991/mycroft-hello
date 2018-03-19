# mycroft-hello
Mycroft Facial Recognition Skill

Introduce yourself to mycroft, and he should remember who you are, and greet you by name.

This skill leverages https://github.com/ageitgey/face_recognition for facial recognition. I have been
unable to get this library to install on my Mark 1 unit, but it runs well on my laptop.

A webcam is reqired for facial recognition.

## Usage:

1. While looking into the camera, greet Mycroft:
   1. "Hey Mycroft, good morning."
   1. "Hey Mycroft, hello."
1. He should greet you, and ask for your name.
   1. Respond with what ever you'd like to be called - the entirety of what you respond with will be used as your name.
1. While looking into the camera, greet Mycroft again.
   1. At this point, he should recognize you, and greet you by name.

This is pretty rough around the edges, but it should be functional.
