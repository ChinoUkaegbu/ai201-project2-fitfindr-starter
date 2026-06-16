from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

# Manual end-to-end agent simulation (for debugging)

if __name__ == "__main__":
    listings = search_listings("graphic tee", max_price=30)

    item = listings[0]
    print("FOUND ITEM:\n", item)

    wardrobe = get_example_wardrobe()
    # wardrobe = get_empty_wardrobe()

    outfit = suggest_outfit(item, wardrobe)

    print("\n--- OUTFIT SUGGESTION ---\n")
    print(outfit)

    fit_card = create_fit_card(outfit, item)
    print("\n--- FIT CARD ---\n")
    print(fit_card)
