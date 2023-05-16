import sqlite3
import streamlit as st
# Connect to SQLite database
conn = sqlite3.connect('recipes.sqlite3')
c = conn.cursor()

def create_table():
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes
        (recipe_title TEXT, recipe TEXT, song_name TEXT, artist TEXT, song_url TEXT)
    ''')

def insert_data(result_dict):
    # Insert a row of data
    c.execute("INSERT INTO recipes VALUES (:recipe_title, :recipe, :song_name, :artist, :song_url)", result_dict)
    # Save (commit) the changes
    conn.commit()
@st.cache_data
def get_records():
    c.execute("SELECT * FROM recipes")
    return c.fetchall()
