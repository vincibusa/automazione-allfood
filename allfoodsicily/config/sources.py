"""List of websites to monitor for food news in Sicily."""

# Generalist Sicilian newspapers (food sections)
GENERALIST_SITES = [
    {
        "name": "Giornale di Sicilia",
        "url": "https://gds.it/food",
        "type": "generalist"
    },
    {
        "name": "LiveSicilia",
        "url": "https://livesicilia.it/food-beverage",
        "type": "generalist"
    },
    {
        "name": "Balarm",
        "url": "https://balarm.it/food",
        "type": "generalist"
    },
    {
        "name": "BlogSicilia",
        "url": "https://blogsicilia.it",
        "type": "generalist"
    }
]

# Specialized food & gastronomy sites
SPECIALIZED_SITES = [
    {
        "name": "Cronache di Gusto",
        "url": "https://cronachedigusto.it",
        "type": "specialized"
    },
    {
        "name": "Sicilia da Gustare",
        "url": "https://siciliadagustare.com",
        "type": "specialized"
    },
    {
        "name": "Culture & Terroir",
        "url": "https://cultureandterroir.com/food",
        "type": "specialized"
    },
    {
        "name": "Sapori e Saperi di Sicilia",
        "url": "https://saporiesaperidisicilia.it/notizie",
        "type": "specialized"
    }
]

# All sites combined
ALL_SITES = GENERALIST_SITES + SPECIALIZED_SITES

# Search queries for Firecrawl Search
SEARCH_QUERIES = [
    "novità food sicilia",
    "ristoranti sicilia",
    "gastronomia siciliana"
]

