"""
Copyright (C) 2016  Christopher Rogers

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger

from time import sleep

import face_recognition
import cv2
import json
import numpy

try:
    from cv2.cv2 import CAP_PROP_FRAME_WIDTH as FRAME_WIDTH, \
                        CAP_PROP_FRAME_HEIGHT as FRAME_HEIGHT, \
                        CAP_PROP_FPS as FPS
except ImportError:
    from cv2.cv import CV_CAP_PROP_FRAME_WIDTH as FRAME_WIDTH, \
                       CV_CAP_PROP_FRAME_HEIGHT as FRAME_HEIGHT, \
                       CV_CAP_PROP_FPS as FPS

from os.path import dirname

__author__ = 'ChristopherRogers1991'

LOGGER = getLogger(__name__)

KNOWN_PERSONS_FILENAME = 'known_persons.json'


class KnownPerson(object):

    def __init__(self, name, encoding):
        self.name = name
        self.encoding = encoding

    def __eq__(self, other):
        return self.name == other.name


class MycroftHelloSkill(MycroftSkill):

    def __init__(self):
        super(MycroftHelloSkill, self).__init__(name="MycroftHelloSkill")
        self.known_persons = set()
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(FPS, 10)

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.load_known_persons()

    @intent_handler(
        IntentBuilder("") \
            .require("Greeting")
    )
    def handle_hello_intent(self, message):
        frame = self.get_gray_frame_from_camera()
        encodings = self.get_face_encodings_from_gray_frame(frame)
        names = self.encodings_to_names(encodings)

        if names:
            data = {'name' : ", ".join(names)}
            self.speak_dialog("known.person.greeting", data)
            return

        self.speak_dialog("unknown.person.greeting")
        if encodings:
            self.handle_unknown_person(encodings)

    def load_known_persons(self):
        if not self.file_system.exists(KNOWN_PERSONS_FILENAME):
            return

        with self.file_system.open(KNOWN_PERSONS_FILENAME, 'r') as persons_file:
            raw_json = persons_file.read()

        person_dict = json.loads(raw_json)
        self.known_persons = {KnownPerson(name, numpy.array(encoding)) for
                              name, encoding in person_dict.iteritems()}

    def write_known_persons_to_disk(self):
        persons_dict = {p.name: p.encoding.tolist() for p in self.known_persons}
        raw_json = json.dumps(persons_dict)
        with self.file_system.open(KNOWN_PERSONS_FILENAME, 'w') as persons_file:
            persons_file.write(raw_json)

    def handle_unknown_person(self, encodings):
        self.speak_dialog("I.dont.recognize.you")
        name = self.get_response("ask.for.name")
        self.new_known_person(name, encodings)

    def new_known_person(self, name, encodings):
        if len(encodings) < 1:
            raise Exception("No visible person!")
        if len(encodings) > 1:
            raise Exception("Too many visible people!")
        data = {"name": name}
        self.speak_dialog("nice.to.meet.you", data)
        self.known_persons.add(KnownPerson(name, encodings[0]))
        self.write_known_persons_to_disk()

    def encodings_to_names(self, encodings):
        if encodings is None:
            return None
        names = []
        for person in self.known_persons:
            matches = face_recognition.compare_faces(encodings, person.encoding)
            if any(matches):
                names.append(person.name)
        return names

    def get_gray_frame_from_camera(self):
        for i in range(3):
            try:
                self.video_capture = cv2.VideoCapture(0)
                ret, frame = self.video_capture.read()
                if ret:
                    break
                sleep(.1)
            except Exception as e:
                pass
        else:
            if e:
                LOGGER.warn("Could not read from camera. Exception was " +
                            str(e))
            return None
        self.video_capture.release()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return gray

    def get_face_encodings_from_gray_frame(self, frame):
        if frame is None:
            return None
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        return face_encodings


def create_skill():
    return MycroftHelloSkill()
