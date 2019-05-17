import os
import sys
from pathlib import Path
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
            prod_template_file = Path(
                os.path.dirname(path) + "/prod_template.yaml")

            if prod_template_file.exists():
                # Open base template
                with open(prod_template_file, 'r') as stream:
                    base_config = yaml.safe_load(stream)

            config: Dict[str, object] = {}

            prod_file = Path(dirname + "/../clientcentral/prod.yaml")
            if prod_file.exists():
                # Open project specific config
                with open(prod_file, 'r') as stream:
                    config = yaml.safe_load(stream)
            else:
                prod_file = Path(os.path.dirname(path) + "/prod.yaml")

                if prod_file.exists():
                    # Open project specific config
                    with open(prod_file, 'r') as stream:
                        config = yaml.safe_load(stream)

            # Merge configs
            if config:
                merged = {**base_config, **config}
            else:
                merged = base_config

            if environ_token and environ_token != "":  # nosec
                merged["token"] = environ_token  # nosec

            return merged
        else:
            base_config = {}

            qa_template_file = Path(
                os.path.dirname(path) + "/qa_template.yaml")
            if qa_template_file.exists():
                # Open base template
                with open(qa_template_file, 'r') as stream:
                    base_config = yaml.safe_load(stream)

            config = {}
            qa_file = Path(dirname + "/../clientcentral/qa.yaml")
            if qa_file.exists():
                # Open project specific config
                with open(qa_file, 'r') as stream:
                    config = yaml.safe_load(stream)
            else:
                qa_file = Path(os.path.dirname(path) + "/qa.yaml")
                if qa_file.exists():
                    # Open project specific config
                    with open(qa_file, 'r') as stream:
                        config = yaml.safe_load(stream)

            # Merge configs
            if config:
                merged = {**base_config, **config}
            else:
                merged = base_config

            if environ_token and environ_token != "":  # nosec
                merged["token"] = environ_token  # nosec

            return merged
