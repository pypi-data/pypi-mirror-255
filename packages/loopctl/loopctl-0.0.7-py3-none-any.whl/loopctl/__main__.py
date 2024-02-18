import os

import fire
from itllib.resources import ResourcePile


class Commander:
    def apply(self, *files, resources="./loop-resources", secrets="./loop-secrets"):
        """Apply the configuration in the given files."""
        resources_path = os.path.realpath(resources)
        secrets_path = os.path.realpath(secrets)

        try:
            # Collect the configs
            prior_configs = ResourcePile(resources_path, secrets_path, read_fully=True)
            new_configs = ResourcePile(*files)

            # Push the updates
            new_configs.apply(prior_configs, resources, secrets_path)

        except ValueError as e:
            print(e)
            print("Fix the errors and try again.")
            return


if __name__ == "__main__":
    fire.Fire(Commander(), name="loopctl")
