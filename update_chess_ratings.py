import requests
import re
import pywikibot

def get_fide_id_from_page(page):
    """
    Extracts the 'fide' parameter from a wiki page.
    
    :param page: Pywikibot page object
    :return: FIDE ID or None if the parameter is not found
    """
    try:
        text = page.text  # Get the page text
        
        # Search for the fide parameter in the page
        fide_match = re.search(r"\|\s*fide\s*=\s*(\d+)", text)
        if fide_match:
            return fide_match.group(1)  # Return FIDE ID
        else:
            return None
    except Exception as e:
        print(f"Error reading page '{page.title()}': {e}")
        return None

def get_ratings(fide_id):
    """
    Extracts the classical, rapid, and blitz ratings for a given fide_id.
    
    :param fide_id: FIDE player ID
    :return: Dictionary with ratings or None if an error occurs
    """
    url = f'https://fide-api.vercel.app/player_history/?fide_id={fide_id}'
    headers = {'accept': 'application/json'}
    
    try:
        # Send GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for errors in the response
        
        data = response.json()  # Convert response to JSON
        
        if data:  # If data is not empty
            first_entry = data[0]  # First entry in the list
            ratings = {
                'classical_rating': first_entry.get('classical_rating', None),
                'rapid_rating': first_entry.get('rapid_rating', None),
                'blitz_rating': first_entry.get('blitz_rating', None),
            }
            # Check if any rating is missing, and if so, return None
            if None in ratings.values():
                return None
            return ratings
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error for FIDE ID {fide_id}: {e}")
        return None

def update_page_with_ratings(page, ratings):
    """
    Updates the wiki page with the ratings.
    
    :param page: Pywikibot page object
    :param ratings: Dictionary containing ratings
    """
    try:
        # Skip if any of the ratings are missing
        if ratings is None:
            print(f"Missing ratings for page '{page.title()}', skipping update.")
            return
        
        text = page.text  # Load the page text
        
        # Update the page with the ratings
        text = re.sub(r"\|\s?classical_rating\s*=.*", f"|classical_rating = {ratings['classical_rating']}", text)
        text = re.sub(r"\|\s?rapid_rating\s*=.*", f"|rapid_rating = {ratings['rapid_rating']}", text)
        text = re.sub(r"\|\s?blitz_rating\s*=.*", f"|blitz_rating = {ratings['blitz_rating']}", text)
        
        # Save changes if any ratings were updated
        page.text = text
        page.save("Updated FIDE ratings.")
        print(f"Ratings successfully saved on page: {page.title()}")
    except Exception as e:
        print(f"Error saving on page '{page.title()}': {e}")

def update_all_pages_in_category(category_name):
    """
    Iterates through all pages in a category and updates their ratings.
    
    :param category_name: The name of the category
    """
    site = pywikibot.Site("chess", "liquipedia")  # Replace with your wiki
    category = pywikibot.Category(site, category_name)
    
    for page in category.articles():
        print(f"Processing page: {page.title()}")
        
        # Get the FIDE ID from the page
        fide_id = get_fide_id_from_page(page)
        if not fide_id:
            print(f"FIDE parameter not found on page: {page.title()}")
            continue
        
        # Get ratings
        ratings = get_ratings(fide_id)
        if not ratings:
            print(f"Failed to get ratings for FIDE ID {fide_id} or missing some ratings.")
            continue
        
        # Update the page with ratings
        update_page_with_ratings(page, ratings)

# Example usage
update_all_pages_in_category("Players")
