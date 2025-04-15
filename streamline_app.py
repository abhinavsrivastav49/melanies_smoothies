# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake and get fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))

# Display DataFrame
st.dataframe(data=my_dataframe, use_container_width=True)

# ❗ FIX: Convert Snowpark DataFrame to a list
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Use the list in the multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
