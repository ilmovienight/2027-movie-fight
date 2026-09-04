import os
import requests

def download_actor_thumbnails():
    # The complete list of actors
    actors = [
        "Ryan Gosling", "Samuel L. Jackson", "George Clooney", "Matt Damon",
        "Brad Pitt", "Denzel Washington", "Harrison Ford", "Leonardo DiCaprio",
        "Nicolas Cage", "Robin Williams", "Morgan Freeman", "Tom Cruise",
        "Rachel McAdams", "Amy Adams", "Julianne Moore", "Emily Blunt",
        "Kirsten Dunst", "Natalie Portman", "Toni Collette", "Emma Stone",
        "Anne Hathaway", "Laura Dern", "Julia Roberts", "Charlize Theron"
    ]

    # Create a directory to save the images
    output_dir = "wikipedia_thumbnails"
    os.makedirs(output_dir, exist_ok=True)

    # Wikipedia API endpoint
    url = "https://en.wikipedia.org/w/api.php"
    
    # Wikipedia requests that automated scripts provide a descriptive User-Agent
    headers = {
        "User-Agent": "ThumbnailDownloader/1.0 (https://en.wikipedia.org/wiki/Main_Page)"
    }

    # Use a session to speed up multiple requests to the same server
    with requests.Session() as session:
        session.headers.update(headers)

        for actor in actors:
            # Parameters for the MediaWiki Action API
            params = {
                "action": "query",
                "titles": actor,
                "prop": "pageimages",
                "format": "json",
                "pithumbsize": 500  # Set the max width of the thumbnail in pixels
            }
            
            try:
                response = session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # The API returns pages under an arbitrary page ID, so we extract the values
                pages = data.get("query", {}).get("pages", {})
                
                for page_id, page_data in pages.items():
                    if "thumbnail" in page_data:
                        img_url = page_data["thumbnail"]["source"]
                        
                        # Download the actual image file
                        img_response = session.get(img_url)
                        img_response.raise_for_status()
                        
                        # Format the filename cleanly (e.g., "Ryan_Gosling.jpg")
                        filename = f"{actor.replace(' ', '_')}.jpg"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Save to disk
                        with open(filepath, "wb") as f:
                            f.write(img_response.content)
                            
                        print(f"✅ Success: Downloaded {filename}")
                    else:
                        print(f"❌ Missing: No thumbnail found for {actor}")
                        
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error: Failed to fetch data for {actor}. Details: {e}")

if __name__ == "__main__":
    print("Starting Wikipedia thumbnail downloads...")
    download_actor_thumbnails()
    print("\nFinished! Check the 'wikipedia_thumbnails' folder.")