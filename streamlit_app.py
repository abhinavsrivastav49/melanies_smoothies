# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name')).to_pandas()
fruit_options = my_dataframe['Fruit_Name'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    # Combine ingredients into a single string
    ingredients_string = ' '.join(ingredients_list).strip()

    # Use parameterized queries for SQL insertion
    my_insert_stmt = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (%s, %s)"
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt, [ingredients_string, name_on_order]).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")

    # Fetch and display nutrition information for selected ingredients
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        
        if smoothiefroot_response.headers.get('Content-Type') == 'application/json':
            json_data = smoothiefroot_response.json()
            if isinstance(json_data, list):  # Assuming the API returns a list of objects
                st.dataframe(data=pd.DataFrame(json_data), use_container_width=True)
            else:
                st.error(f"Could not display nutrition info for {fruit_chosen}.")
        else:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")
