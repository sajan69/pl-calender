import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import xml.etree.ElementTree as ET


def scrape_onefootball_fixtures():
    url = "https://onefootball.com/en/competition/premier-league-9/fixtures"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    fixtures = []
    
    for match_day in soup.find_all('ul', class_='MatchCardsList_matches__8_UwB'):
        # Extract matches within the match day
        for match in match_day.find_all('a', class_='MatchCard_matchCard__iOv4G'):
            # Extract home and away teams
            home_team = match.find('span', class_='SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D').text.strip()
            away_team = match.find_all('span', class_='SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')[1].text.strip()
            
            # Extract date and time from the <time> elements
            time_element = match.find('time', class_='title-8-bold')
            if time_element:
                match_time = time_element['datetime']  # Get the datetime attribute
                match_date = datetime.fromisoformat(match_time[:-1])  # Remove 'Z' and convert to datetime
                formatted_date = match_date.strftime("%d/%m/%Y")
                formatted_time = match_date.strftime("%H:%M")
            else:
                formatted_date = 'Unknown Date'
                formatted_time = 'Unknown Time'

            # Extract status if available
            status_element = match.find('span', class_='SimpleMatchCard_simpleMatchCard__infoMessage___NJqW')
            status = status_element.text.strip() if status_element else 'Unknown Status'
            
            print(f"Date: {formatted_date}, Time: {formatted_time}, Home Team: {home_team}, Away Team: {away_team}, Status: {status}")
            
            fixtures.append({
                'date': formatted_date,
                'time': formatted_time,
                'home_team': home_team,
                'away_team': away_team,
                'status': status
            })
    
    return fixtures


def create_ics_file(fixtures, filename):
    # Initialize the calendar
    cal = Calendar()
    
    

    for fixture in fixtures:
        
        
        event = Event()
        event.add('summary', f"{fixture['home_team']} vs {fixture['away_team']}")
        
        # Combine date and time into a single datetime object
        date_str = f"{fixture['date']} {fixture['time']}"
        start_time = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        start_time = pytz.utc.localize(start_time)
        
        # Add event details
        event.add('dtstart', start_time)
        event.add('dtend', start_time + timedelta(hours=2))  # Assume 2 hours duration
        event.add('description', f"Status: {fixture['status']}")
        
       
        # Add the event to the calendar
        cal.add_component(event)

    # Create directory if it doesn't exist
    directory = Path.cwd() / 'ICS_Files'
    directory.mkdir(parents=True, exist_ok=True)

    # Write to disk
    with open(os.path.join(directory, filename), 'wb') as f:
        f.write(cal.to_ical())



def main():
    fixtures = scrape_onefootball_fixtures()
    print(f"fixtures: {fixtures}")
    create_ics_file(fixtures, 'premier_league_fixtures.ics')
    print(f"Created ICS file with {len(fixtures)} fixtures.")
   

if __name__ == "__main__":
    main()