from dataclasses import  dataclass
from dataclasses_json import dataclass_json
import argparse
from .Error import ZonevuError
import os


@dataclass_json
@dataclass
class EndPoint:
    apikey: str
    verify: bool = False
    base_url: str = 'zonevu.ubiterra.com'

    @classmethod
    def from_key(cls, apiKey: str) -> 'EndPoint':
        return cls(apiKey)

    @classmethod
    def from_keyfile(cls) -> 'EndPoint':
        """
        Creates an EndPoint instance from a json file whose path is provided in the command line.
        User either -k or --keyfile to pass in as an argument the path to the key json file.
        Here is an example key json file:
        {
            "apikey": "xxxx-xxxxx-xxxxx-xxxx"
        }
        @return: An Endpoint instance
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-k", "--keyfile", type=str)  # Path/Filename to key file
        args, unknown = parser.parse_known_args()
        key_path = args.keyfile
        if key_path is None:
            raise ZonevuError.local('the parameter --keyfile must be specified in the command line')

        if not os.path.exists(key_path):
            raise ZonevuError.local('keyfile "%s" not found' % key_path)

        with open(key_path, 'r') as file:
            args_json = file.read()
            instance = cls.from_json(args_json)
            return instance
