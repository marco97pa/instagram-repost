#!/usr/bin/env python3
import sys
import os
import yaml
from instagrapi import Client
from PIL import Image
import requests

OVERLAY = "overlay.png"
skip_post = True

# Init
cl = Client()

def load_sources():
    """Reads the data.yaml YAML file

    Data about sources and latest post is stored inside the data.yaml file in the same directory as the script

    Returns:
      A dictionary that contains all the sources and last update time
    """

    print("Loading data from YAML file...")

    with open('data.yaml', encoding="utf-8") as file:
        sources = yaml.load(file, Loader=yaml.FullLoader)

        out = ""
        for source in sources:
            out += source["name"]
            out += ", "
        print("Sources: {}".format(out))

        return sources

def write_sources(sources):
    """Writes the data.yaml YAML file

     Data about sources and latest post is stored inside the data.yaml file in the same directory as the script

    Args:
      sources: dictionary that contains all the sources and last update time
    """

    print("Writing data to YAML file...")
    with open('data.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(sources, file, sort_keys=False, allow_unicode=True)


def instagram_last_post(source, user_id):
    """Gets the last post of a profile

    It posts if there is a new post: if the timestamp of the latest stored post does not match with the latest fetched posts timestamp

    Args:
      - user_id: a profile ID
      - source: a dictionary with all the details of the source

    Returns:
      an dictionary containing all the updated data of the source
    """

    print("({}) Fetching new posts".format(source["name"]))

    medias = cl.user_medias(user_id, 5)
    
    for media in medias:
        # If the last post timestamp is greater (post is newest) or the saved post does not exist
        if "last_post" not in source or media.taken_at.timestamp() > source["last_post"]:
            link = "https://www.instagram.com/p/" + media.code
            # If there is only one element in the post (it's not an album)
            if media.media_type != 8:
                # If this is a video
                if media.media_type == 2:
                    content_type = "video"
                    filename = "temp.mp4"
                    url = "{}".format(media.video_url)
                    download(url, filename)
                    print("{} posted a new {} on Instagram, at {} - Link: {}".format(source["name"], content_type, media.taken_at.timestamp(), link))
                    if not skip_post:
                        cl.video_upload(
                            filename,
                            clean_caption(media.caption_text)
                        )
                    delete_files(filename)
                # If this is a photo
                if media.media_type == 1:
                    content_type = "photo"
                    filename = "temp.jpg"
                    url = "{}".format(media.thumbnail_url)
                    download(url, filename)
                    edit_image(filename, OVERLAY)
                    print("{} posted a new {} on Instagram, at {} - Link: {}".format(source["name"], content_type, media.taken_at.timestamp(), link))
                    if not skip_post:
                        cl.photo_upload(
                            filename,
                            clean_caption(media.caption_text)
                        )
                    delete_files(filename)
            # If this is an album, a collection of photos and videos
            else:
                content_type = "collection"
                i = 0
                filenames = []
                # Get all the elements of the collection
                for resource in media.resources:
                    i=i+1
                    # If it's an image
                    if resource.media_type == 1:
                        filename = "temp{}.jpg".format(i)
                        url = "{}".format(resource.thumbnail_url)
                        download(url, filename)
                        edit_image(filename, OVERLAY)
                    # If it's a video
                    else:
                        filename = "temp{}.mp4".format(i)
                        url = "{}".format(resource.video_url)
                        download(url, filename)
                    filenames.append(filename)
                print("{} posted a new {} of {} medias on Instagram, at {} - Link: {}".format(source["name"], content_type, i, media.taken_at.timestamp(), link))
                if not skip_post:
                    cl.album_upload(
                        filenames,
                        clean_caption(media.caption_text)
                    )
                delete_files(filenames)

        # Save last post timestamp
        if media.taken_at.timestamp() > source["last_post"]:
            source["last_post"] = media.taken_at.timestamp()
    return source

def instagram_profile(username):
    """Gets the details of an account on Instagram

    Args
      username: a string with the nickname of the account

    Returns:
      - a Profile ID
    """

    print("({}) Fetching details".format(username))
    user_id = cl.user_id_from_username(username)
    return user_id


def clean_caption(caption):
    """Removes unnecessary parts of an Instagram post caption

    It removes all the hashtags and converts tags in plain text (ex: @marco97pa --> marco97pa)

    Args:
      caption: a text

    Returns:
      the same caption without hashtags and tags
    """

    clean = ""

    words = caption.split()
    for word in words:
        if word[0] != "#":
            if word[0] == "@":
                clean += word[1:] + " "
            else:
                clean += word + " "

    return clean

def download(url, filename):
    """Downloads a file, given an url and filename

    Args:
      url: source from where download the image
      filename: name of the file to save
    """
    
    response = requests.get(url)

    file = open(filename, "wb")
    file.write(response.content)
    file.close()

    return filename

def delete_files(file_list):
    """Deletes all files from a list

    Args:
      file_list: a list of files or a string of the path of a single file
    """

    # Ensure file_list is a list
    if isinstance(file_list, str):
        file_list = [file_list]

    for file_path in file_list:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def edit_image(base_image_path, overlay_image_path):
    """Adds an overlay to an image on the top left corner
       and overwrites it

    Args:
      base_image_path: image to add the overlay, will be overwritten
      overlay_image_path: the overlay to add
    """
    # Open the base image
    base_image = Image.open(base_image_path)
    
    # Open the overlay image
    overlay_image = Image.open(overlay_image_path)
    
    # Paste the overlay image on the base image at the top-left corner (0, 0)
    base_image.paste(overlay_image, (0, 0), overlay_image)
    
    # Save the result
    base_image.save(base_image_path)


# Main code
if __name__ == '__main__':
    
    # Show an error if no username and password are passed
    if len(sys.argv) < 3:
        print("Usage: python script.py <username> <password>")
        print("Optional arguments: --no-post to skip posting on Instagram")
        sys.exit(1)

    if sys.argv[3] == "--no-post":
        skip_post = True

    # Get Instagram username and password
    ACCOUNT_USERNAME = sys.argv[1]
    ACCOUNT_PASSWORD = sys.argv[2]

    # Login
    cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)

    # Load sources (Instagram pages name and latest updates)
    sources = load_sources()

    # Get the last post from all the sources above and eventually repost it
    for source in sources:
        user_id = instagram_profile(source["name"])
        source = instagram_last_post(source, user_id)

    write_sources(sources)
    
