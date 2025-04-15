# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake and fetch fruit options
cnx = st.connection("snowflake")
session = cnx.session()
fruit_options = [row['Fruit_Name'] for row in session.table("smoothies.public.fruit_options").select(col('Fruit_Name')).collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    # Combine selected ingredients into a single string
    ingredients_string = ' '.join(ingredients_list).strip()

    # SQL query to insert smoothie order
    my_insert_stmt = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (%s, %s)"
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Execute the SQL query when the button is clicked
        session.sql(my_insert_stmt, [ingredients_string, name_on_order]).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")

    # Fetch and display nutrition information for each selected ingredient
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        # Make API call to fetch nutrition information
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        
        if smoothiefroot_response.headers.get('Content-Type') == 'application/json':
            try:
                json_data = smoothiefroot_response.json()
                if isinstance(json_data, dict):  # Render dictionary data as key-value pairs
                    for key, value in json_data.items():
                        st.write(f"**{key}:** {value}")
                elif isinstance(json_data, list):  # Render list data
                    for item in json_data:
                        st.write(item)
                else:
                    st.error(f"Could not display nutrition info for {fruit_chosen}. Unexpected format.")
            except ValueError:
                st.error(f"Invalid JSON response for {fruit_chosen}.")
        else:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")
