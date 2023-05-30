import os
import re
import urllib.parse
import openai
import spotipy
import streamlit as st
from streamlit.components import v1 as components
from spotipy.oauth2 import SpotifyClientCredentials
import base64
from PIL import Image
from io import BytesIO
import random
from concurrent.futures import ThreadPoolExecutor

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['SPOTIFY_CLIENT_ID'] = st.secrets['SPOTIFY_CLIENT_ID']
os.environ['SPOTIFY_CLIENT_SECRET'] = st.secrets['SPOTIFY_CLIENT_SECRET']

openai.api_key = os.environ['OPENAI_API_KEY']
client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                      client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_recipe_and_wine(prompt_ingredients, prompt_dietary_requirement, prompt_cuisine):
    while True:
        try:

            prompt = f"""As a creative chef, you are renowned for your unique and innovative dishes. Given the ingredients {', '.join(prompt_ingredients)}, create a unique and exciting recipe that reflects the {prompt_cuisine} cuisine and complies with the {prompt_dietary_requirement} dietary requirement. Avoid common dishes such as stews, soups or casseroles. Remember to include the cooking method, the preparation steps, and presentation ideas. Also, suggest a wine pairing and suggest a South African wine by brand specifically if possible, and complimentary spices and herbs. Show the estimated calories per portion. Use these subheadings it the results: 'Ingredients:', 'Instructions:', 'Wine pairing:','South African wine recommendation:','Complimentary spices and herbs:', 'Estimated calories per portion:'. Give the recipe a name and use it as a title indicated by 'Title:'.Use centigrade for temperature and grams for weight."""

            recipe_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a creative chef renowned for your innovative dishes."},
                          {"role": "user", "content": f"{prompt}"}],
                temperature=0.7,
                max_tokens=500,
            )
            results = recipe_completion['choices'][0]['message']['content']
            print(results)
            return results
        except (openai.error.InvalidRequestError, openai.error.APIConnectionError, openai.error.AuthenticationError, openai.error.APIError, openai.error.RateLimitError) as e:
            print(e)
            continue


def create_db_dict(db_title, recipe, song_name, db_artist, db_song_url):
    result_dict = {
        'recipe_title': db_title,
        'recipe': recipe,
        'song_name': song_name,
        'artist': db_artist,
        'song_url': db_song_url
    }
    return result_dict

def return_random_song(genre):

    while True:
        try:

            query = f"genre%3A{genre}&type=playlist&market=ZA"
            playlists = sp.search(q=query, type='playlist', market='ZA', limit=10)
            playlist_items = playlists['playlists']['items']

            # Raise an exception if no playlists are found
            if not playlist_items:
                raise ValueError(f"No playlists found for genre {genre}")

            # Try to select a playlist and track
            for _ in range(len(playlist_items)):
                random_playlist = random.choice(playlist_items)
                playlist_id = random_playlist['id']
                selector_playlist_url = random_playlist['external_urls']['spotify']
                tracks = sp.playlist_items(playlist_id)
                track_items = tracks['items']

                # If the playlist has no tracks, remove it from the list and try again
                if not track_items:
                    playlist_items.remove(random_playlist)
                    continue

                random_track = random.choice(track_items)
                track_name = random_track['track']['name']
                track_artist = random_track['track']['artists'][0]['name']
                track_url = random_track['track']['external_urls']['spotify']
                return track_name, track_artist, track_url, selector_playlist_url

            # Raise an exception if no tracks are found in any of the playlists
            raise ValueError(f"No tracks found in playlists for genre {genre}")

        except (spotipy.client.SpotifyException, spotipy.SpotifyException) as e:
            print(e)
            continue

def get_genre(cuisine):
    while True:
        try:

            prompt = f"Return a list of five Spotify genres that relate to {cuisine}. Return the result in the form of a Python" \
                     f"list object: [genre1,genre2,genre3]."
            genre_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful DJ"},
                          {"role": "user", "content": f"{prompt}"}],
                temperature=0.1,
                max_tokens=50,
            )
            s = genre_completion['choices'][0]['message']['content']
            match = re.search(r'\[.*?]', s)

            if match:
                extracted_list_str = match.group(0)
                extracted_list = eval(extracted_list_str)
                genre_recommendation = random.choice(extracted_list)
                return genre_recommendation
            else:
                raise ValueError("AI response does not contain a genre list in the expected format")
        except (openai.error.InvalidRequestError, openai.error.APIConnectionError, openai.error.AuthenticationError, openai.error.APIError, openai.error.RateLimitError) as e:
            print(e)
            continue

# def return_random_song(genre):
#     # Choose a genre
#     query = f"genre%3A{genre}&type=playlist&market=ZA"
#     # Get playlists of the genre
#     playlists = sp.search(q=query, type='playlist', market='ZA', limit=10)
#
#     playlist_items = playlists['playlists']['items']
#     random_track = None
#     # Choose a random track
#     while random_track is None:
#         try:
#             # Choose a random playlist
#             random_playlist = random.choice(playlist_items)
#             playlist_id = random_playlist['id']
#             # get playlist url
#             selector_playlist_url = random_playlist['external_urls']['spotify']
#             #st.write(selector_playlist_url)
#             # Get the tracks in the playlist
#             tracks = sp.playlist_items(playlist_id)
#             track_items = tracks['items']
#
#             # Choose a random track
#             random_track = random.choice(track_items)
#             track_name = random_track['track']['name']
#             track_artist = random_track['track']['artists'][0]['name']
#             # get song url
#             track_url = random_track['track']['external_urls']['spotify']
#             return track_name, track_artist, track_url, selector_playlist_url
#         except IndexError:
#             continue
#

# def get_genre(cuisine):
#     prompt = f"Return a list of five Spotify genres that relate to {cuisine}. Return the result in the form of a Python" \
#              f"list object: [genre1,genre2,genre3]."
#     genre_completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "system", "content": "You are a helpful DJ"},
#                   {"role": "user", "content": f"{prompt}"}],
#         temperature=0.1,
#         max_tokens=50,
#     )
#     s = genre_completion['choices'][0]['message']['content']
#     #st.write(s)
#     match = re.search(r'\[.*?]', s)
#
#     if match:
#         # extract the list from the string
#         extracted_list_str = match.group(0)
#
#         # convert the extracted string to a list
#         extracted_list = eval(extracted_list_str)
#         genre_recommendation = random.choice(extracted_list)
#         return genre_recommendation
#     else:
#         genre_completion = random.choice(
#             ['World', 'World Chill', 'Vocal Jazz', 'Roots Reggae', 'Soul', 'Soul Jazz', 'Salsa', ])


def generate_whatsapp_url(text):
    base_url = "https://wa.me/?text="
    encoded_text = urllib.parse.quote(text)
    return f"{base_url}{encoded_text}"


def format_subheadings(result_text):
    subheadings = [
        "Title:",
        "Ingredients:",
        "Instructions:",
        "Wine pairing:",
        "South African wine recommendation:",
        "Complimentary spices and herbs:",
        "Estimated calories per portion:",
        "Song recommendation:",
    ]

    lines = result_text.split("\n")
    for i, line in enumerate(lines):
        for subheading in subheadings:
            if subheading in line:
                if subheading == "Title:":
                    line = line.replace(subheading, "")
                    lines[i] = f"<h3>{line.strip()}</h3>"
                else:
                    lines[i] = line.replace(subheading, f"<b>{subheading}</b>")
                break

    return "\n".join(lines)


def extract_title(result_text):
    lines = result_text.split("\n")
    for i, line in enumerate(lines):
        if "Title:" in line:
            line = line.replace("Title:", "")
            return line.strip()


def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_base64}"


st.set_page_config(page_title="DineVineVibe", layout="centered", page_icon="🍷")

# Include Bootstrap CDN
st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" 
integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">""",
            unsafe_allow_html=True)

st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

background_image = "veggies.jpg"
background_image_base64 = image_to_base64(background_image)

# Custom CSS
custom_css = f"""
<style>body {{
        background-image: url({background_image_base64});
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    h1 {{
        font-family: 'Roboto', sans-serif;
        color: #25D366;
    }}

    button {{
        font-family: 'Roboto', sans-serif;
    }}

    .btn {{
        background-color: #25D366;
        color: white;
        font-family: 'Roboto', sans-serif;
        border: none;
        padding: 10px 20px;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
        border-radius: 25px
    }}
</style>"""

st.markdown(custom_css, unsafe_allow_html=True)

# Create columns for layout
left_column, center_column, right_column = st.columns([1, 3, 1])

with center_column:
    st.title("DineVineVibe")
    st.markdown("<p style='color: red;'>Under Development</p>", unsafe_allow_html=True)
    st.markdown("""<p> Enter ingredients and we'll make a recipe for you, suggest a wine pairing (and SA one 
    specifically, because that's how we roll!) - and even come up with a Spotify song to cook and dine to! </p> 
    <p>Recipes are built by an AI not Gordon Ramsey so use common sense if something looks odd.</p>""",
                unsafe_allow_html=True)
    ingredients = st.text_input("Enter ingredients (comma-separated):")
    cuisines = [
        'Italian', "African",'Chinese', 'Indian', 'Mexican', 'Japanese',
        'Middle Eastern', 'Thai', 'American', 'Greek', 'French', 'Spanish'
    ]
    cuisine = st.selectbox("Select a cuisine:", cuisines)
    options = ['Anything goes', 'Keto', 'Low fat', 'Under 300 calories', 'Vegetarian', 'Vegan', 'Gluten-free']
    dietary_requirement = st.selectbox("Select a dietary requirement:", options)

    if st.button("Find Recipe and Wine Pairing"):
        if ingredients == "":
            st.error("Please enter ingredients.")
            st.stop()
        if "," not in ingredients:
            st.error("Please enter ingredients separated by commas.")
            st.stop()
        else:
            ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]
            #result = get_recipe_and_wine(ingredients_list, dietary_requirement, cuisine)
            with ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(get_recipe_and_wine, ingredients_list, dietary_requirement,
                                          cuisine)
                future2 = executor.submit(get_genre, cuisine)
                result = future1.result()
                genre_result = future2.result()
                formatted_result = format_subheadings(result)
                #genre_result = get_genre(cuisine)
            try:
                song, artist, song_url, playlist_url = return_random_song(genre_result)
            except KeyError:
                song, artist, song_url, playlist_url = return_random_song("World")
            line = f"Song recommendation: {song} by {artist} from genre {genre_result} and from this <a href='{playlist_url}' target='_blank'>playlist</a>"
            spotify_spot = st.empty()
            formatted_result = formatted_result + "\n\n" + format_subheadings(line)
            st.markdown(formatted_result, unsafe_allow_html=True)
            whatsapp_url = generate_whatsapp_url(result)
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="btn">Share by WhatsApp</a>',
                        unsafe_allow_html=True)
            # Convert the Spotify URL to Spotify Embed URL
            song_embed_url = song_url.replace("open.spotify.com/track", "open.spotify.com/embed/track")

            # Embed Spotify song using HTML iframe
            spotify_spot = components.html(
                f'<iframe src="{song_embed_url}" width="95%" height="380" frameborder="0" allowtransparency="true" '
                f'allow="encrypted-media"></iframe>',
                height=400
            )
            # st.markdown(f'<a href="{song_url}" target="_blank" class="btn">Listen to Song</a>',
            #            unsafe_allow_html=True)
            title = extract_title(result)
            record = create_db_dict(title, result, song, artist, song_url)
