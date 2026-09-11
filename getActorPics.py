import os
import re
import requests


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
    data = session.get(api, params=params, timeout=30).json()
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
    info_data = session.get(api, params=info_params, timeout=30).json()
    info_page = info_data["query"]["pages"][0]
    if "imageinfo" not in info_page:
        print(f"❌ Missing: no image info for '{filename}'")
        return False

    file_info = info_page["imageinfo"][0]
    img_url = file_info.get("thumburl") or file_info["url"]

    img_response = session.get(img_url, timeout=60)
    img_response.raise_for_status()

    filepath = os.path.join(output_dir, f"{clean_filename(title)}.jpg")
    with open(filepath, "wb") as f:
        f.write(img_response.content)

    print(f"✅ Success: {title} -> {filepath}")
    return True


def download_actor_photo(name: str, session, output_dir: str) -> bool:
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
    data = session.get(api, params=params, timeout=30).json()
    page = data["query"]["pages"][0]

    if page.get("missing"):
        print(f"❌ Missing: '{name}' has no Wikipedia article")
        return False
    if "thumbnail" not in page:
        print(f"❌ Missing: no photo found for '{name}'")
        return False

    img_url = page["thumbnail"]["source"]
    img_response = session.get(img_url, timeout=60)
    img_response.raise_for_status()

    filepath = os.path.join(output_dir, f"{clean_filename(name)}.jpg")
    with open(filepath, "wb") as f:
        f.write(img_response.content)

    print(f"✅ Success: {name} -> {filepath}")
    return True


TMDB_POSTERS = {
    "Children of Men": "k9IAS4TehZFcKi4HVByxZNPfqex",
}


def download_tmdb_poster(title: str, poster_path: str, session, output_dir: str) -> bool:
    url = f"https://media.themoviedb.org/t/p/w780/{poster_path}.jpg"
    img_response = session.get(url, timeout=60)
    img_response.raise_for_status()

    filepath = os.path.join(output_dir, f"{clean_filename(title)}.jpg")
    with open(filepath, "wb") as f:
        f.write(img_response.content)

    print(f"✅ Success: {title} -> {filepath}")
    return True


def main():
    movies = [
        "Les Misérables (2012 film)",
        "The Devil Wears Prada (film)",
        "Ella Enchanted (film)",
        "The Princess Diaries (film)",
        "Interstellar (film)",
        "Brokeback Mountain",
        "Blue Velvet (film)",
        "Jurassic Park (film)",
        "Year of the Dog (film)",
        "Marriage Story",
        "Little Women (2019 film)",
        "Is This Thing On?",
        "A Quiet Place (film)",
        "Edge of Tomorrow",
        "Sicario (2015 film)",
        "Into the Woods (2014 film)",
        "The Smashing Machine (2025 film)",
        "The Big Lebowski",
        "Boogie Nights",
        "The Fugitive (1993 film)",
        "Safe (1995 film)",
        "Hannibal (2001 film)",
        "Children of Men",
        "Good Will Hunting",
        "Aladdin (1992 Disney film)",
        "Mrs. Doubtfire",
        "Dead Poets Society",
        "Jumanji (film)",
        "Flubber (film)",
        "Moonstruck",
        "Leaving Las Vegas",
        "The Rock (film)",
        "Raising Arizona",
        "Lord of War",
        "Valley Girl (1983 film)",
        "Ocean's Eleven",
        "Michael Clayton (film)",
        "Fantastic Mr. Fox (film)",
        "O Brother, Where Art Thou?",
        "Burn After Reading",
        "Up in the Air (2009 film)",
        "The Bourne Identity (2002 film)",
        "The Departed",
        "The Martian (film)",
        "The Talented Mr. Ripley (film)",
    ]

    actors = [
        "George Clooney",
        "Matt Damon",
        "Nicolas Cage",
        "Robin Williams",
        "Julianne Moore",
        "Emily Blunt",
        "Anne Hathaway",
        "Laura Dern",
        "Brad Pitt",
        "Denzel Washington",
        "Morgan Freeman",
        "Tom Cruise",
        "Kirsten Dunst",
        "Glenn Close",
        "Julia Roberts",
        "Charlize Theron",
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