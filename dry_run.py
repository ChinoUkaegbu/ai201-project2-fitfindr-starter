from tools import search_listings, suggest_outfit
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

if __name__ == "__main__":
    listings = search_listings("graphic tee", max_price=30)
    print("FOUND ITEM:\n", listings[0])

    wardrobe = get_example_wardrobe()
    # wardrobe = get_empty_wardrobe()

    result = suggest_outfit(listings[0], wardrobe)

    print("\n--- OUTFIT SUGGESTION ---\n")
    print(result)
