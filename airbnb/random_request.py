import random
import uuid
import os


class RandomRequest(object):

    @classmethod
    def get_random_user_agent(cls):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/supported_ios_versions.txt')) as f:
            ios_versions = f.read().splitlines()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/airbnb_versions.txt')) as f:
            airbnb_versions = f.read().splitlines()

        return "Airbnb/{} iPhone/{} Type/Phone".format(random.choice(airbnb_versions), random.choice(ios_versions))

    @classmethod
    def get_random_udid(cls):
        hex_digits = "0123456789abcdef"
        return ''.join(random.choice(hex_digits) for _ in range(40))

    @classmethod
    def get_random_uuid(cls):
        return str(uuid.uuid4()).upper()
