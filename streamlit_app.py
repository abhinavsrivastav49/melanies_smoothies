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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'))

# Convert Snowflake data to pandas DataFrame for easier handling
pd_df = pd.DataFrame([row.as_dict() for row in my_dataframe.collect()])  # Convert to DataFrame

# Get the list of fruits from the DataFrame
fruit_list = pd_df['FRUIT_NAME'].tolist()

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
                                
                                # Add a new column (e.g., "Source")
                                row["Source"] = "SmoothieFroot API"  # Static value for now
                                
                                rows.append(row)

                        # Convert the rows to a pandas DataFrame for easier display
                        nutrition_df = pd.DataFrame(rows)

                        # Display nutrition info as a table using pandas DataFrame
                        if not nutrition_df.empty:
                            st.table(nutrition_df)
                        else:
                            st.warning(f"No nutritional information found for {fruit_chosen}.")
                        
                        # Additional command to display search value for the chosen fruit
                        try:
                            # Search for the 'SEARCH_ON' value associated with the chosen fruit
                            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
                            st.write(f'The search value for {fruit_chosen} is {search_on}.')
                        except IndexError:
                            st.warning(f"No 'SEARCH_ON' value found for {fruit_chosen}.")
                    else:
                        st.warning(f"Unexpected response format for {fruit_chosen}. Missing 'nutrition' data.")
                except Exception as e:
                    st.error(f"Error parsing data for {fruit_chosen}: {e}")
            else:
                st.error(f"Failed to fetch nutrition info for {fruit_chosen}. HTTP status: {response.status_code}")
