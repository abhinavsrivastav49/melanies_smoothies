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
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]  # Extract values

# Multiselect for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

# Handle order submission
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie has been ordered, {name_on_order}!", icon="✅")

        # Fetch and display nutrition info per fruit
        for fruit_chosen in ingredients_list:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")

            if smoothiefroot_response.status_code == 200:
                try:
                    json_data = smoothiefroot_response.json()
                    st.subheader(f"{fruit_chosen} Nutrition Information")

                    # Ensure data is a list
                    if isinstance(json_data, list) and len(json_data) > 0:
                        fruit_data = json_data[0]

                        # Extract nutrition values (e.g., carbs, fat)
                        nutrients = ['carbs', 'fat', 'protein', 'calories']
                        rows = []

                        for nutrient in nutrients:
                            if nutrient in fruit_data:
                                row = {
                                    "Nutrient": nutrient,
                                    "Family": fruit_data.get("family", ""),
                                    "Genus": fruit_data.get("genus", ""),
                                    "ID": fruit_data.get("id", ""),
                                    "Name": fruit_data.get("name", ""),
                                    "Nutrition": fruit_data[nutrient],
                                    "Order": fruit_data.get("order", "")
                                }
                                rows.append(row)

                        if rows:
                            st.table(rows)
                        else:
                            st.warning(f"No recognizable nutrients found for {fruit_chosen}.")
                    else:
                        st.warning(f"Unexpected response format for {fruit_chosen}.")

                except Exception as e:
                    st.error(f"Error parsing data for {fruit_chosen}: {e}")
            else:
                st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")
