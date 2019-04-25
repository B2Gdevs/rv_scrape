"""
The app used to scrape and download images from websites.

This is targeted at crestviewrv.com right now.

Author: Benjamin Garrard
Date: 4/25/2019
"""
import uuid
from os import path
import os
import requests
import time
import sys
import traceback
import utils
import argparse


def download_images(driver, url, save_dir, common_string="unit_photo"):
    """
    Download the images from the given listing url.

    Parameters
    ----------
    driver: Web ChromeDriver
        The driver for the browser from selenium.
    url: str
        The url of the listing.  This url must be for one listing.
    save_dir: str
        The directory where the images are saved.
    common_string: str
        This is a string that is common amongst the picture urls.  This is 
        to alleviate some of the iterations and make sure only relevant photos
        are downloaded.

    """
    driver.get(url)
    images = driver.find_elements_by_tag_name("img")
    for image in images:
        image_url = image.get_attribute("src")
        if image_url:
            if image_url.lower().endswith((".jpg", ".png")):
                if image_url.find(common_string) != -1:
                    download_image(image_url, save_dir)


def download_image(url, save_dir):
    """
    Download the image from the url.

    Parameters
    ----------
    url: str
        The url the image is located.  This is the url that if put in a browser
        will only show the image.
    save_dir: str
        The directory where images should be saved at.

    """
    ext = path.splitext(url)[1]
    image_path = path.join(save_dir, "rv_image{}{}".format(uuid.uuid4(), ext))

    with open(image_path, 'wb') as file:
        img_data = requests.get(url).content
        file.write(img_data)


def get_listing_urls(driver, yaml_dict):
    """
    Get the total amount of pages to scrape on the website.

    Parameters
    ----------
    driver: WebChrome Driver
        The driver that is used to drive the Chrome browser.
    yaml_dict: dict
        The dict that houses the config variables set in the config file.

    Returns
    -------
    urls: list
        The all of the listing urls on the page that the driver is on.

    """
    prev_count = 0
    new_count = None
    while prev_count != new_count:
        units = driver.find_elements_by_css_selector(
                       yaml_dict["listing_url_selector"])
        prev_count = len(units)

        # Scroll to the bottom of the page just in case infinite scrollig is on
        driver.execute_script(
               "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        units = driver.find_elements_by_css_selector(
                       yaml_dict["listing_url_selector"])
        new_count = len(units)

    urls = []
    for unit in units:
        urls.append(unit.get_attribute(yaml_dict["listing_url_attr"]))

    return urls


def get_total_pages(driver, yaml_dict):
    """
    Get the total amount of pages to scrape on the website.

    Parameters
    ----------
    driver: WebChrome Driver
        The driver that is used to drive the Chrome browser.
    yaml_dict: dict
        The dict that houses the config variables set in the config file.

    Returns
    -------
    total: int
        The total amount of pages that must be scraped to fully scrape the
        website.

    """
    total_items = driver.find_elements_by_css_selector(
                  yaml_dict["total_css_selector"])
    total = int(total_items[0].text)//yaml_dict["listings_per_page"]
    return total + 1  # they start with 1 instead of 0


def run_app(yaml_dict):
    """
    Run the application and scrape a website.

    Checkpoints will be saved periodically if there are any errors.  There will
    be a save file created for when the application completes the scrape to 
    indicate that the scraping has been done accordingly.

    Parameters
    ----------
    yaml_dict: dict
        The dict that holds the config variables found in a config file.  The
        config files should be located in your configs directory.

    """
    driver = utils.initialize_driver()
    save_dir = path.join(yaml_dict["save_path"], yaml_dict["save_dir"])
    listing_urls_path = path.join(save_dir, "listing_urls")
    url_index_path = path.join(save_dir, "url_index")

    os.makedirs(save_dir, exist_ok=True)
    driver.get(yaml_dict["url"])

    pages = get_total_pages(driver, yaml_dict)

    if path.exists(listing_urls_path):
        listing_urls = utils.load_binary(listing_urls_path)
    else:
        listing_urls = []

        for page_num in range(pages):
            driver.get(yaml_dict["url"] + "?page={}".format(page_num))
            listing_urls.extend(get_listing_urls(driver, yaml_dict))

        utils.save_binary(listing_urls_path, listing_urls)

    if path.exists(url_index_path):
        index = utils.load_binary(url_index_path)
        print("Starting from index {}".format(index))
    else:
        index = 0

    for i in range(index, len(listing_urls)):
        try:
            download_images(driver, listing_urls[i], save_dir)
        except Exception as e:
            print("Exception occurred")
            traceback.print_exc()
            print("Saved index at {}".format(i))
            utils.save_binary(url_index_path, i)
            sys.exit(0)

        utils.save_binary(url_index_path, i)  # Final index save


def get_args():
    """Get commandline arguments."""
    parser = argparse.ArgumentParser(description="Scrapes websites" +
                                                 "Google's Speech API.")

    parser.add_argument("-rs", "--restart", action="store_true",
                        help="Restarts the process and clears checkpoints.")
    parser.add_argument("-c", action="store_true",
                        help="Continues the program where it left off. There" +
                             "could've been an error thrown.")
    parser.add_argument("--config", help="Config file to use other than " +
                        "default")

    args = parser.parse_args()

    return args


def main():
    """Use config variables to setup and and run app."""
    args = get_args()

    if args.config:
        yaml_dict = utils.load_yaml(args.config)
    else:
        yaml_dict = utils.load_yaml()  # Get from default file

    save_path = os.path.join(yaml_dict["save_path"], yaml_dict["save_dir"])

    if utils.is_completed(save_path):
        if args.c:
            print("Scrape already completed for this URL")
            print("Shutting down program")
            sys.exit(0)
        elif args.restart:
            utils.delete_saves(save_path)
            run_app(yaml_dict)
    else:
        if args.c:
            run_app(yaml_dict)
        elif args.restart:
            utils.delete_saves(save_path)
            run_app(yaml_dict)
        else:
            if os.path.exists(save_path):
                print("Specify the continue flag with -c to continue.")
            else:
                print("Running app for first time on URL")
                run_app(yaml_dict)

    utils.complete_scrape(save_path)


if __name__ == "__main__":
    main()
