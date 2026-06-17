"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────


def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()
    query_words = set(re.findall(r"\w+", description.lower()))

    scored_results = []

    for listing in listings:

        # Price filter
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter
        if size is not None:
            if size.lower() not in listing["size"].lower():
                continue

        searchable_text = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                " ".join(listing["style_tags"]),
                " ".join(listing["colors"]),
                listing["brand"] or "",
            ]
        ).lower()

        score = sum(1 for word in query_words if word in searchable_text)

        if score > 0:
            scored_results.append((score, listing))

    scored_results.sort(key=lambda result: result[0], reverse=True)

    return [listing for score, listing in scored_results]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    wardrobe_items = wardrobe.get("items", [])

    item_info = f"""
Title: {new_item['title']}
Category: {new_item['category']}
Description: {new_item['description']}
Style Tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}
Condition: {new_item['condition']}
"""

    # Empty wardrobe case
    if not wardrobe_items:
        prompt = f"""
You are a fashion stylist.

The user is considering buying this thrifted item:

{item_info}

The user has not provided any wardrobe items.

Suggest 1-2 outfit ideas for styling this piece.
Explain what kinds of bottoms, shoes, outerwear, or accessories pair well with it.
Keep the response concise (2-4 short paragraphs).
"""
    else:
        wardrobe_text = "\n\n".join(f"""
Name: {item['name']}
Category: {item['category']}
Colors: {', '.join(item['colors'])}
Style Tags: {', '.join(item['style_tags'])}
Notes: {item.get('notes') or 'None'}
""".strip() for item in wardrobe_items)

        prompt = f"""
You are a fashion stylist.

The user owns the following wardrobe items:

{wardrobe_text}

The user is considering buying this thrifted item:

{item_info}

Create 1-2 complete outfits using the thrifted item and specific pieces from the wardrobe.

Requirements:
- Refer to wardrobe items by name.
- Explain why the pieces work together.
- Mention the overall style or vibe.
- Keep the response concise.
"""
    client = _get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────


def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # 1. Guard clause (IMPORTANT)
    if not outfit or outfit.strip() == "":
        return "Error: Cannot generate fit card because outfit suggestion is missing or incomplete."

    item_info = f"""
Item: {new_item['title']}
Price: ${new_item['price']}
Platform: {new_item['platform']}
Category: {new_item['category']}
Colors: {', '.join(new_item['colors'])}
Style Tags: {', '.join(new_item['style_tags'])}
"""

    prompt = f"""
You are a social media fashion content creator.

Write a 2–4 sentence Instagram/TikTok caption for an outfit post.

The post is based on this thrifted item:

{item_info}

The outfit styling is:
{outfit}

Requirements:
- Casual, authentic OOTD vibe
- Mention the item name, price, and platform naturally (exactly once each)
- Describe the outfit vibe clearly
- Do NOT sound like a product description
- Make it feel like a real social media post
"""

    client = _get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,  # higher randomness for varied captions
    )

    return response.choices[0].message.content.strip()


# ── Tool 4: assess_price_fairness ───────────────────────────────────────────────────
def assess_price_fairness(item: dict, listings: list[dict]) -> str:
    """
    Compare the price of an item against similar listings in the dataset
    and return a human-readable fairness assessment.

    Similarity is defined as:
        - same category
        - AND at least one overlapping style tag

    Fallback:
        - if no style-tag matches exist, fall back to category-only matches
        - if still none, return a "not enough data" message

    Args:
        item:     The listing dict for the thrifted item.
        listings: A list containing all the listings in the database.

    Returns:
        A string indicating whether the price is "fair", "expensive", or "cheap"
        relative to similar items, along with a brief explanation.
    """
    if not item or not listings:
        return "Not enough data to assess pricing."

    item_price = item.get("price", 0)
    item_category = item.get("category", "")
    item_tags = set(item.get("style_tags", []))

    # ── Step 1: Find similar items ─────────────────────────────
    similar = [
        l
        for l in listings
        if l.get("category") == item_category
        and len(item_tags & set(l.get("style_tags", []))) > 0
        and l.get("price") is not None
    ]

    # ── Fallback: relax filter if too strict ───────────────────
    if len(similar) < 3:
        similar = [
            l
            for l in listings
            if l.get("category") == item_category and l.get("price") is not None
        ]

    # ── Final fallback: nothing to compare ─────────────────────
    if not similar:
        return (
            "Not enough comparable items in the dataset to assess pricing "
            "for this category."
        )

    # ── Step 2: Extract prices ────────────────────────────────
    prices = [l["price"] for l in similar if isinstance(l.get("price"), (int, float))]

    if not prices:
        return "Not enough valid price data to assess pricing."

    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    # ── Step 3: Determine pricing label ───────────────────────
    if item_price < avg_price * 0.85:
        label = "cheap"
    elif item_price > avg_price * 1.15:
        label = "expensive"
    else:
        label = "fair"

    # ── Step 4: Pick a few examples ───────────────────────────
    examples = sorted(similar, key=lambda x: abs(x["price"] - item_price))[:3]

    example_text = "\n".join(f"- {e['title']} — ${e['price']:.0f}" for e in examples)

    # ── Step 5: Build explanation ─────────────────────────────
    return (
        f"This item is considered {label} based on similar listings.\n\n"
        f"Comparable items in the dataset range from ${min_price:.0f} "
        f"to ${max_price:.0f}, with an average of ${avg_price:.0f}.\n\n"
        f"Closest examples:\n{example_text}\n\n"
        f"At ${item_price:.0f}, this listing is {label} relative to the market."
    )
