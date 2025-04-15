import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd  # Import pandas as pd

# Streamlit App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection (use correct connection settings)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name', 'SEARCH_ON'))

# Convert Snowflake data to pandas DataFrame for easier handling
pd_df = pd.DataFrame([row.as_dict() for row in my_dataframe.collect()])  # Convert to DataFrame

# Get the list of fruits from the DataFrame
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

# Initialize ingredients string
ingredients_string = ""

# Handle order submission
if ingredients_list:
    # Build the ingredients string
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '

        # Get the 'SEARCH_ON' value for the current fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Display nutritional information for each fruit
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetching the data from the SmoothieFroot API (updated endpoint)
        smoothie_froot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothie_froot_response.status_code == 200:
            try:
                smoothie_froot_data = smoothie_froot_response.json()

                # Show the nutritional information as a table
                st.dataframe(smoothie_froot_data, use_container_width=True)
            except Exception as e:
                st.error(f"Error parsing SmoothieFroot data for {fruit_chosen}: {e}")
        else:
            st.error(f"Failed to fetch SmoothieFroot data for {fruit_chosen}. HTTP status: {smoothie_froot_response.status_code}")

    # Final string for ingredients
    st.write(f"Your selected ingredients: {ingredients_string[:-2]}")  # Remove the last comma and space
