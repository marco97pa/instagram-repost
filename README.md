# instagram-repost
A Python script that reposts content from one or more Instagram account(s) to yours.  
It can also add an overlay on the reposted photos, for example your logo, to further personalize it.

## Installation and configuration
To use **instagram-repost** you need to have Python 3.9+ installed or use pyenv (the version is setting accordingly automatically).  
- Clone the repository
- Run `pip install -r requirements.txt`
- Create or copy an **overlay.png** file: this image will be the overlay to add to the photos reposted
- Create a **data.yaml** file with the list of Instagram accounts to observe, following [this template](data_example.yaml):

```
- name: instagram
- name: teslamotors
...
```

## First launch
During the first launch the script will collect the last 5 posts of each account to be observed and will repost them.  
If you don't want to repost them during the first app launch, just run this command:
`python main.py <username> <password> --no-post`  
Username and password are your Instagram credentials.  
After the first execution the **data.yaml** file is populated with the timestamp of the last post.

## Usage
You can check for new posts of the accounts you observe and (eventually) repost them by typing:  
`python main.py <username> <password>`  
Where username and password are your Instagram credentials.  
**Additional arguments:**  
- `--no-post` avoid posting on Instagram but still execute the code. Useful for testing or first app launch.
- `--no-overlay` if you don't need to add an overlay to the reposted photos
