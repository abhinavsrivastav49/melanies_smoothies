# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title and instructions
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names from the table and turn into a list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Multiselect with max 5
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Submit button
    if st.button('Submit Order'):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")

    # Show nutrition info for each selected fruit using JSON viewer
    for fruit in ingredients_list:
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit}")
        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            try:
                json_data = response.json()
                st.subheader(f"Nutrition Info: {fruit}")
                st.json(json_data)
            except ValueError:
                st.error(f"Could not parse nutrition info for {fruit}.")
        else:
            st.error(f"Failed to fetch nutrition info for {fruit}.")
