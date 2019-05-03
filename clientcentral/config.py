import os
import sys
from typing import Any, Dict

import yaml

dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
path = os.path.abspath(__file__)


class Config:

    production: bool = False

    def __init__(self, production: bool) -> None:
        self.production = production

    def get(self) -> Dict[str, Any]:
        environ_token = None
        try:
            environ_token = os.environ['CC_TOKEN']
        except KeyError:
            pass

        if self.production:
            base_config: Dict[str, object] = {}
            if os.path.exists(os.path.dirname(path) + "/prod_template.yaml"):
                # Open base template
                with open(os.path.dirname(path) + "/prod_template.yaml",
                          'r') as stream:
                    base_config = yaml.safe_load(stream)

            config: Dict[str, object] = {}
            if os.path.exists(dirname + "/../clientcentral/prod.yaml"):
                # Open project specific config
                with open(dirname + "/../clientcentral/prod.yaml",
                          'r') as stream:
                    config = yaml.safe_load(stream)
            else:
                if os.path.exists(os.path.dirname(path) + "/prod.yaml"):
                    # Open project specific config
                    with open(os.path.dirname(path) + "/prod.yaml",
                              'r') as stream:
                        config = yaml.safe_load(stream)

            # Merge configs
            if config:
                merged = {**base_config, **config}
            else:
                merged = base_config

            if environ_token and environ_token != "":
                merged["token"] = environ_token

            return merged
        else:
            base_config = {}
            if os.path.exists(os.path.dirname(path) + "/qa_template.yaml"):
                # Open base template
                with open(os.path.dirname(path) + "/qa_template.yaml",
                          'r') as stream:
                    base_config = yaml.safe_load(stream)

            config = {}
            if os.path.exists(dirname + "/../clientcentral/qa.yaml"):
                # Open project specific config
                with open(dirname + "/../clientcentral/qa.yaml",
                          'r') as stream:
                    config = yaml.safe_load(stream)
            else:
                if os.path.exists(os.path.dirname(path) + "/qa.yaml"):
                    # Open project specific config
                    with open(os.path.dirname(path) + "/qa.yaml",
                              'r') as stream:
                        config = yaml.safe_load(stream)

            # Merge configs
            if config:
                merged = {**base_config, **config}
            else:
                merged = base_config

            if environ_token and environ_token != "":
                merged["token"] = environ_token

            return merged
