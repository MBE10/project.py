import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import database  



def scrape_movie(title: str, added_by: str = "scraper") -> Optional[Dict]:
    query = title.replace(" ", "+")
    url = f"https://www.imdb.com/find/?q={query}"

    try:
        r = requests.get(url)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    result = soup.select_one("td.result_text a")
    if not result:
        return None

    movie_link = "https://www.imdb.com" + result.get("href").split("?")[0]

    try:
        r = requests.get(movie_link)
        r.raise_for_status()
    except Exception:
        return None

    movie_page = BeautifulSoup(r.text, "html.parser")

    title_tag = movie_page.select_one("h1")
    year_tag = movie_page.select_one("span.sc-8c396aa2-2")
    summary_tag = movie_page.select_one("span.sc-466bb6c-2")
    director_tag = movie_page.select_one("a.ipc-metadata-list-item__list-content-item")

    clean_title = title_tag.text.strip() if title_tag else title
    clean_year = None
    if year_tag:
        try:
            clean_year = int(year_tag.text.strip().replace("(", "").replace(")", ""))
        except:
            clean_year = None

    clean_desc = summary_tag.text.strip() if summary_tag else ""
    clean_director = director_tag.text.strip() if director_tag else ""

    movie_data = {
        "title": clean_title,
        "year": clean_year,
        "director": clean_director,
        "description": clean_desc,
        "added_by": added_by
    }

    saved = database.create_movie(movie_data)
    return saved


def scrape_many(titles: list, added_by: str = "scraper") -> list:
    results = []
    for t in titles:
        m = scrape_movie(t, added_by)
        if m:
            results.append(m)
    return results


if __name__ == "__main__":
    test = scrape_movie("Inception", "system")
    print(test)
