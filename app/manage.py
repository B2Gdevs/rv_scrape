import os
import sys
import argparse
import yaml


def create_new_config():
    config = {
        "listing_url_selector": "",
        "save_dir": "",
        "url": "",
        "save_path": "../images",
        "listings_per_page": 25,
        "total_css_selector": "",
        "listing_url_attr": "href"
    }
    return config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manages the project.")

    parser.add_argument("--create_config",
                        help="Restarts the process and clears checkpoints.")
    parser.add_argument("-c", action="store_true",
                        help="Continues the program where it left off. There" +
                             "could've been an error thrown.")
    parser.add_argument("--config", help="Config file to use other than " +
                        "default")

    args = parser.parse_args()

    if args.create_config:
        file_path = os.path.join("configs", args.create_config + ".yaml")
        if os.path.exists(file_path):
            print("Config file already exists.  Exiting program")
            sys.exit(0)
        else:
            with open(file_path, 'w') as file:
                yaml.dump(create_new_config(), file, default_flow_style=False)
