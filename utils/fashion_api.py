def get_fashion_suggestions(query: str):
    """
    Dummy fashion API mock.
    Replace this with real fashion APIs later (Nykaa, Myntra, etc).
    """
    suggestions = {
        "pink dress": ["Pink Sequin Party Dress", "Rose Satin Gown", "Blush Bodycon Dress"],
        "black shoes": ["Black Heels", "Classic Black Boots", "Black Loafers"]
    }
    return suggestions.get(query.lower(), ["No direct match found. Try accessories!"])
