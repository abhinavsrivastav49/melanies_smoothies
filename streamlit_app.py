# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Streamlit App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]  # Extract values for multiselect

# Multiselect box
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

# Submit logic
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")

        # Fetch and display nutrition info for each fruit
        for fruit_chosen in ingredients_list:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")

            if smoothiefroot_response.status_code == 200:
                try:
                    json_data = smoothiefroot_response.json()
                    st.subheader(f"{fruit_chosen} Nutrition Information")
                    
                    if isinstance(json_data, dict):
                        st.table([json_data])  # wrap in list to render single-row table
                    elif isinstance(json_data, list):
                        st.table(json_data)
                    else:
                        st.warning(f"Unexpected data format for {fruit_chosen}.")
                except Exception as e:
                    st.error(f"Error parsing nutrition info for {fruit_chosen}: {e}")
            else:
                st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")
