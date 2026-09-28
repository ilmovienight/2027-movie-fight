import os
import re
import time
import requests


def get_raw(session, url, **kwargs):
    for attempt in range(6):
        resp = session.get(url, **kwargs)
        if resp.status_code == 429:
            time.sleep(min(30, 2 ** attempt))
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def clean_filename(name: str) -> str:
    return name.replace("/", "_").replace("\\", "_").replace(" ", "_")


def get_infobox_image(text: str):
    m = re.search(r"(?im)^\s*\|\s*image\s*=\s*(.+?)\s*$", text)
    if not m:
        return None
    value = m.group(1).strip()
    linked = re.match(r"\[\[\s*file\s*:\s*([^|\]]+)", value, re.I)
    if linked:
        return linked.group(1).strip()
    return value


def download_poster(title: str, session, output_dir: str) -> bool:
    filepath = os.path.join(output_dir, f"{clean_filename(title)}.jpg")
    if os.path.exists(filepath):
        print(f"⏭️ Skip: {title} already exists")
        return True

    api = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "redirects": 1,
        "formatversion": 2,
        "format": "json",
    }
    data = get_raw(session, api, params=params, timeout=30).json()
    page = data["query"]["pages"][0]

    if page.get("missing"):
        print(f"❌ Missing: '{title}' has no Wikipedia article")
        return False

    content = page["revisions"][0]["slots"]["main"]["content"]
    filename = get_infobox_image(content)
    if not filename:
        print(f"❌ Missing: no infobox image found for '{title}'")
        return False

    info_params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 500,
        "redirects": 1,
        "formatversion": 2,
        "format": "json",
    }
    info_data = get_raw(session, api, params=info_params, timeout=30).json()
    info_page = info_data["query"]["pages"][0]
    if "imageinfo" not in info_page:
        print(f"❌ Missing: no image info for '{filename}'")
        return False

    file_info = info_page["imageinfo"][0]
    img_url = file_info.get("thumburl") or file_info["url"]

    img_response = get_raw(session, img_url, timeout=60)

    with open(filepath, "wb") as f:
        f.write(img_response.content)

    time.sleep(1)
    print(f"✅ Success: {title} -> {filepath}")
    return True


def download_actor_photo(name: str, session, output_dir: str) -> bool:
    filepath = os.path.join(output_dir, f"{clean_filename(name)}.jpg")
    if os.path.exists(filepath):
        print(f"⏭️ Skip: {name} already exists")
        return True

    api = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "pithumbsize": 500,
        "redirects": 1,
        "formatversion": 2,
        "format": "json",
    }
    data = get_raw(session, api, params=params, timeout=30).json()
    page = data["query"]["pages"][0]

    if page.get("missing"):
        print(f"❌ Missing: '{name}' has no Wikipedia article")
        return False
    if "thumbnail" not in page:
        print(f"❌ Missing: no photo found for '{name}'")
        return False

    img_url = page["thumbnail"]["source"]
    img_response = get_raw(session, img_url, timeout=60)

    with open(filepath, "wb") as f:
        f.write(img_response.content)

    time.sleep(1)
    print(f"✅ Success: {name} -> {filepath}")
    return True


TMDB_POSTERS = {
    "Children of Men": "k9IAS4TehZFcKi4HVByxZNPfqex",
}


def download_tmdb_poster(title: str, poster_path: str, session, output_dir: str) -> bool:
    filepath = os.path.join(output_dir, f"{clean_filename(title)}.jpg")
    if os.path.exists(filepath):
        print(f"⏭️ Skip: {title} already exists")
        return True

    url = f"https://media.themoviedb.org/t/p/w780/{poster_path}.jpg"
    img_response = get_raw(session, url, timeout=60)

    with open(filepath, "wb") as f:
        f.write(img_response.content)

    time.sleep(1)
    print(f"✅ Success: {title} -> {filepath}")
    return True


def main():
    movies = [
        "Burn After Reading",
        "Inglourious Basterds",
        "Fight Club (film)",
        "Ocean's Eleven (film)",
        "Seven (1995 film)",
        "Moneyball (film)",
        "Training Day (film)",
        "Fences (film)",
        "Remember the Titans",
        "Mississippi Masala",
        "Philadelphia (film)",
        "Flight (2012 film)",
        "Bruce Almighty (film)",
        "The Shawshank Redemption",
        "The Dark Knight (film)",
        "Million Dollar Baby (film)",
        "Lucky Number Slevin",
        "101 Dalmatians (film)",
        "Dangerous Liaisons",
        "The Big Chill (film)",
        "Tarzan (1999 film)",
        "The Wife (2017 film)",
        "Fatal Attraction",
        "Pretty Woman (film)",
        "Erin Brockovich (film)",
        "Notting Hill (film)",
        "Steel Magnolias",
        "Hook (film)",
        "Monster (2003 film)",
        "Mad Max: Fury Road",
        "The Italian Job (2003 film)",
        "The Cider House Rules",
        "Snow White and the Huntsman",
        "Prometheus (2012 film)",
        "Mission: Impossible (film)",
        "Top Gun (film)",
        "Jerry Maguire",
        "Rain Man",
        "A Few Good Men (film)",
        "Magnolia (film)",
        "Little Women (2019 film)",
        "Spider-Man (2002 film)",
        "Melancholia (2011 film)",
        "Elizabethtown (film)",
        "Kiki's Delivery Service",
        "Jumanji (film)"
    ]

    actors = [
    ]

    output_dir = "wikipedia_thumbnails"
    actor_dir = "actor_thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(actor_dir, exist_ok=True)

    headers = {
        "User-Agent": "MoviePosterDownloader/1.0 (https://github.com/movie-night; admin@example.org)"
    }

    with requests.Session() as session:
        session.headers.update(headers)
        for title in dict.fromkeys(movies):
            try:
                if title in TMDB_POSTERS:
                    download_tmdb_poster(title, TMDB_POSTERS[title], session, output_dir)
                else:
                    download_poster(title, session, output_dir)
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error: failed to fetch '{title}'. Details: {e}")

        for name in dict.fromkeys(actors):
            try:
                download_actor_photo(name, session, actor_dir)
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error: failed to fetch '{name}'. Details: {e}")


if __name__ == "__main__":
    print("Starting movie poster and actor photo downloads...")
    main()
    print("\nFinished! Check the 'wikipedia_thumbnails' and 'actor_thumbnails' folders.")