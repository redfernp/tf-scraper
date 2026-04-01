"""
Timeform Tip Sheet Scraper
Scrapes best bets from: https://www.timeform.com/horse-racing/tips/free-tip-sheet-best-bets-tomorrow
Extracts: Meeting name, Race time, Horse name, Odds (fractional)
"""

import requests
from bs4 import BeautifulSoup


URL = "https://www.timeform.com/horse-racing/tips/free-tip-sheet-best-bets-tomorrow"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def scrape_tips():
    """Scrape Timeform tip sheet and return structured data."""
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    meetings = []

    for meeting_section in soup.find_all("section", class_="w-tip-sheet-meeting"):
        # Meeting name from h2 inside the header div
        header = meeting_section.find("div", class_="w-tip-sheet-header")
        if not header:
            continue
        h2 = header.find("h2")
        if not h2:
            continue

        # The h2 contains "ChepstowFree Tips" — extract just the venue name
        # by getting the first text node before "Free Tips"
        meeting_name = h2.get_text(strip=True).replace("Free Tips", "").strip()

        races = []
        for race_div in meeting_section.find_all("div", class_="w-tip-sheet-race"):
            # Time
            time_el = race_div.find("a", class_="w-tip-sheet-race-time")
            if not time_el:
                continue
            race_time = time_el.get_text(strip=True)

            # Horse name (strip country suffix like "(IRE)")
            horse_div = race_div.find("div", class_="w-tip-sheet-race-horse")
            if not horse_div:
                continue
            horse_link = horse_div.find("a")
            if horse_link:
                raw_name = horse_link.get_text(strip=True)
            else:
                raw_name = horse_div.get_text(strip=True)
            # Remove country codes like (IRE), (GB), (FR), etc.
            horse_name = raw_name.split("(")[0].strip()

            # Odds — first visible fractional price (Paddy Power is first, non-hidden)
            price_div = race_div.find("div", class_="w-tip-sheet-race-price")
            odds = ""
            if price_div:
                # Find the first price link that is NOT hidden
                for price_link in price_div.find_all("a", class_="price"):
                    classes = price_link.get("class", [])
                    if "hide" in classes:
                        continue
                    frac = price_link.find("span", class_="price-fractional")
                    if frac:
                        odds = frac.get_text(strip=True)
                        break

            races.append({
                "time": race_time,
                "horse": horse_name,
                "odds": odds,
            })

        meetings.append({
            "meeting": meeting_name,
            "races": races,
        })

    return meetings


def format_output(meetings):
    """Format meetings data as plain text output."""
    lines = []
    for meeting in meetings:
        lines.append(meeting["meeting"])
        for race in meeting["races"]:
            lines.append(f"{race['time']} {race['horse']} {race['odds']}")
        lines.append("")  # blank line between meetings
    return "\n".join(lines).strip()


if __name__ == "__main__":
    tips = scrape_tips()
    if not tips:
        print("No tips found — the page may not have tomorrow's tips yet.")
    else:
        print(format_output(tips))
