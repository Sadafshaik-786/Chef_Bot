import os
import requests
import chainlit as cl
from dotenv import load_dotenv

# Load env variables
load_dotenv()
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

# API endpoints
FIND_BY_INGREDIENTS_URL = "https://api.spoonacular.com/recipes/findByIngredients"
RECIPE_INFO_URL = "https://api.spoonacular.com/recipes/{id}/information"

def get_recipes_with_ingredients(ingredients, limit=3):
    """Fetch recipes, sorted by best match and include nutrition info."""
    try:
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "ingredients": ingredients,
            "number": limit * 2,   # fetch more, then filter/sort
            "ranking": 1           # maximize used ingredients
        }
        res = requests.get(FIND_BY_INGREDIENTS_URL, params=params)
        print("Status:", res.status_code)

        if res.status_code != 200:
            print("API Error:", res.text)
            return []

        data = res.json()

        # Sort by: highest usedIngredientCount, lowest missedIngredientCount
        sorted_data = sorted(
            data,
            key=lambda x: (-x.get("usedIngredientCount", 0), x.get("missedIngredientCount", 0))
        )

        recipes = []
        for item in sorted_data[:limit]:
            recipe_id = item.get("id")
            title = item.get("title", "No title")
            image = item.get("image", "")

            # Fetch full recipe info (with nutrition)
            info_res = requests.get(
                RECIPE_INFO_URL.format(id=recipe_id),
                params={"apiKey": SPOONACULAR_API_KEY, "includeNutrition": "true"}
            )

            if info_res.status_code == 200:
                info = info_res.json()
                recipe_url = info.get("sourceUrl", "#")
                ingredients_list = [ing["original"] for ing in info.get("extendedIngredients", [])]

                # Extract calories and nutrition
                nutrition = info.get("nutrition", {})
                nutrients = nutrition.get("nutrients", [])
                calories = next((n["amount"] for n in nutrients if n["name"] == "Calories"), None)

                # Build small table for macros (cal, protein, fat, carbs)
                macros = {}
                for key in ["Calories", "Protein", "Fat", "Carbohydrates"]:
                    val = next((n for n in nutrients if n["name"] == key), None)
                    if val:
                        macros[key] = f"{val['amount']} {val['unit']}"

                nutrition_table = "| Nutrient | Amount |\n|----------|--------|\n"
                for k, v in macros.items():
                    nutrition_table += f"| {k} | {v} |\n"

            else:
                recipe_url = "#"
                ingredients_list = []
                calories = None
                nutrition_table = ""

            recipes.append({
                "title": title,
                "image": image,
                "url": recipe_url,
                "ingredients": ingredients_list,
                "calories": calories,
                "nutrition_table": nutrition_table
            })

        return recipes
    except Exception as e:
        print("Error:", e)
        return []

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content.strip()

    # Fetch recipes
    recipes = get_recipes_with_ingredients(user_input, limit=3)

    if recipes:
        for recipe in recipes:
            ingredients_text = "\n".join([f"- {ing}" for ing in recipe["ingredients"]])

            cal_text = f"🔥 {recipe['calories']} kcal" if recipe["calories"] else ""

            await cl.Message(
                content=(
                    f"🍽 **{recipe['title']}** {cal_text}\n"
                    f"🔗 [View Recipe]({recipe['url']})\n\n"
                    f"**Ingredients:**\n{ingredients_text}\n\n"
                    f"**Nutrition Info:**\n{recipe['nutrition_table']}"
                ),
                elements=[
                    cl.Image(
                        name=recipe['title'],
                        display="inline",
                        url=recipe['image'],
                        description=recipe['title']
                    )
                ]
            ).send()
    else:
        await cl.Message(
            content=f"😞 Sorry, I couldn’t find recipes for '{user_input}'."
        ).send()
