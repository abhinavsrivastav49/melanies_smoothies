import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Streamlit App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection (use correct connection settings)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('search_on'))
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
            # Fetching the data from the API
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Ensure data is a dictionary and contains "nutrition" key
                    if isinstance(data, dict) and "nutrition" in data:
                        st.subheader(f"{fruit_chosen} Nutrition Information")

                        # Extract metadata (if available)
                        metadata = {
                            "Family": data.get("family", "N/A"),
                            "Genus": data.get("genus", "N/A"),
                            "ID": data.get("id", "N/A"),
                            "Name": data.get("name", "N/A"),
                            "Order": data.get("order", "N/A")
                        }

                        # Extract nutrients from the nested "nutrition" key
                        nutrition_data = data.get("nutrition", {})
                        nutrients = ["carbs", "fat", "protein", "sugar"]  # sugar included as well
                        
                        # Prepare rows where nutrients will be shown in rows, and metadata in columns
                        rows = []
                        for nutrient in nutrients:
                            if nutrient in nutrition_data:
                                row = {
                                    "Nutrient": nutrient.capitalize(),
                                    "Value": nutrition_data[nutrient]
                                }
                                # Add metadata as columns
                                for key, value in metadata.items():
                                    row[key] = value
                                rows.append(row)

                        # Display nutrition info in a transposed table (nutrients in rows, metadata in columns)
                        if rows:
                            # Show the table with nutrients in rows and metadata in columns
                            st.table(rows)
                        else:
                            st.warning(f"No nutritional information found for {fruit_chosen}.")
                    else:
                        st.warning(f"Unexpected response format for {fruit_chosen}. Missing 'nutrition' data.")
                except Exception as e:
                    st.error(f"Error parsing data for {fruit_chosen}: {e}")
            else:
                st.error(f"Failed to fetch nutrition info for {fruit_chosen}. HTTP status: {response.status_code}")
