from tools import (
    assess_price_fairness,
    create_fit_card,
    search_listings,
    suggest_outfit,
)
from utils.data_loader import get_empty_wardrobe, get_example_wardrobe, load_listings


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []  # empty list, no exception


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_empty_wardrobe():
    item = search_listings("graphic tee")[0]
    wardrobe = get_empty_wardrobe()

    result = suggest_outfit(item, wardrobe)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_suggest_outfit_with_wardrobe():
    item = search_listings("graphic tee")[0]
    wardrobe = get_example_wardrobe()

    result = suggest_outfit(item, wardrobe)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_create_fit_card_empty_outfit():
    listings = load_listings()
    item = listings[0]

    result = create_fit_card("", item)

    assert isinstance(result, str)
    assert "error" in result.lower()


def test_create_fit_card_whitespace_outfit():
    listings = load_listings()
    item = listings[1]

    result = create_fit_card("   ", item)

    assert isinstance(result, str)
    assert "error" in result.lower()


def test_create_fit_card_valid_outfit():
    listings = load_listings()
    item = listings[2]

    outfit = "Pair with baggy jeans, sneakers, and a denim jacket."

    result = create_fit_card(outfit, item)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_assess_price_fairness_returns_string():
    listings = load_listings()
    item = listings[0]

    result = assess_price_fairness(item, listings)

    assert isinstance(result, str)
    assert len(result.strip()) > 0
