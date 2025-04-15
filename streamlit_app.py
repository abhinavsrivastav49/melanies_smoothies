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
from snowflake.snowpark.session import Session

connection_parameters = {
    "account": "<your_account>",
    "user": "<your_username>",
    "password": "<your_password>",
    "role": "<your_role>",
    "warehouse": "<your_warehouse>",
    "database": "<your_database>",
    "schema": "<your_schema>"
}
session = Session.builder.configs(connection_parameters).create()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))

# Display DataFrame
st.dataframe(data=my_dataframe.to_pandas(), use_container_width=True)

# ❗ FIX: Convert Snowpark DataFrame to a list
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Use the list in the multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options
)

if len(ingredients_list) > 5:
    st.error("You can only select up to 5 ingredients.")

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # Button to trigger order submission
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            # Use a parameterized insert to prevent SQL injection
            session.table("smoothies.public.orders").insert(
                [{"ingredients": ingredients_string, "name_on_order": name_on_order}]
            )
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while placing the order: {e}")

import requests
try:
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    smoothiefroot_response.raise_for_status()  # Raise an exception for HTTP errors
    api_data = smoothiefroot_response.json()
    st.dataframe(data=api_data, use_container_width=True)
except requests.exceptions.RequestException as e:
    st.error(f"Failed to fetch data from the API: {e}")
