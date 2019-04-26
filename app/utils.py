import os
import datetime
import selenium
from selenium.webdriver.chrome.options import Options
import pickle
from yaml import Loader, Dumper, load, dump


def load_yaml(file_name="rv_config.yaml"):
    """
    Load yaml config file for RV Scraping.

    Parameters
    ----------
    file_dir_name: str
        The name of the directory where the images are being saved.  This also
        is where all other information like checkpoints are being saved.

    Returns
    -------
    yaml_dict : dict
        A dictionary containing config variables.

    """
    global save_path
    file_name = os.path.join("configs", file_name + ".yaml")
    with open(file_name, 'r') as file:
        yaml_dict = load(file, Loader=Loader)
        save_path = yaml_dict["save_path"]

    return yaml_dict


def save_binary(save_path, obj, verbose=True):
    """
    Save the object in to a binary file for later use.

    Parameters
    ----------
    save_path: str
        The path where to save the binary file.
    obj: object
        The object to be saved as a binary file.
    verbose:
        Boolean that if true lets the user know if the file was saved.

    Returns
    -------
    obj
        The object that was saved

    """
    with open(save_path, "wb") as file:
        pickle.dump(obj, file)

    if verbose:
        print("{} has been saved at {}.".format(os.path.basename(save_path),
                                                save_path))
    return obj


def load_binary(file_path, verbose=True):
    """
    Load a binary file in to an object.

    Parameters
    ----------
    file_path: str
        The path to where the binary file is.
    verbose:
        Boolean that if true lets the user know if the object was loaded.

    Returns
    -------
    obj
        The object that was loaded

    """
    with open(file_path, "rb") as file:
        obj = pickle.load(file)

    if verbose:
        print("{} has been loaded from {}.".format(os.path.basename(file_path),
                                                   file_path))
    return obj


def initialize_driver(options=[], headless=True):
    """
    Initialize the webdriver to be used in the app.

    Parameters
    ----------
    options: list
        A list of options that can be passed to Chrome Options.  This includes
        making the selenium driver headless.
    headless: bool
        The option to be able to see the browser in action or not.  If True
        then the browser will not be visible.

    Returns
    -------
    driver: WebChrome Driver
        The driver that selenium uses to operate the browser.

    """
    ops = Options()
    if "headless" not in options:
        if headless:
            ops.add_argument("--headless")
    for op in options:
        ops.add_argument("--{}".format(op))
    driver = selenium.webdriver.Chrome(options=ops)
    driver.implicitly_wait(20)

    return driver


def is_completed(save_path):
    """
    Check to see if scrape has already been completed

    Parameters
    ----------
    save_dir: str
        The save directory where every image and checkpoint will be saved.

    Returns
    -------
    bool
        The boolean that says if the scrape has already been completed before.

    """
    path = os.path.join(save_path, ".save")

    if os.path.exists(path):
        return True
    return False


def complete_scrape(save_path):
    """
    Create a save file that marks if the scrape has been completed.

    Parameters
    ----------
    save_dir: str
        The save directory name to put the .save file.

    """
    path = os.path.join(save_path, ".save")
    with open(path, "w") as file:
        file.write("Scrape Completed {}".format(datetime.datetime.now()))

    print("Program has finished scraping the website.")


def delete_saves(save_path):
    """
    Delete all checkpoints within the directory.

    Parameters
    ----------
    save_dir: str
        The path to the save directory where images and checkpoints are saved.

    """
    save_file_path = os.path.join(save_path, ".save")
    index_file_path = os.path.join(save_path, "url_index")
    url_file_path = os.path.join(save_path, "listing_urls")

    if os.path.exists(save_file_path):
        os.remove(save_file_path)

    if os.path.exists(index_file_path):
        os.remove(index_file_path)

    if os.path.exists(url_file_path):
        os.remove(url_file_path)

    print("Deleted checkpoints")
