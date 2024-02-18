import argparse


class Input:
    @staticmethod
    def get_name_from_args(title: str = '') -> str:
        # Get a name from argument list or ask user for it
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", type=str)  # Input well
        args, unknown = parser.parse_known_args()
        name = args.name

        # Not found in argument list so ask user
        if name is None:
            name = input("Enter %s name: " % title)  # Get name from user in console

        return name
