# Chess_ratings_liquipedia
Script for updating fide ratings on liquipedia pages

- Goes through all "Players" category pages
- Looks for a `fide` parameter and gets the ratings through the API
- Fills/updates `rapid_rating, blitz_rating, classical_rating` parameters on player's page
  - Skips parameter if it doesn't exist
