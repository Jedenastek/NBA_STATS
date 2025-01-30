from pickle import FALSE
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import time
from pyfiglet import Figlet
from io import StringIO
from term_image.image import *
import re


figlet = Figlet()

#selenium driver options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.minimize_window()

#all urls used in this project
p_s_url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'
team_url = 'https://www.basketball-reference.com/teams/{}/{}.html'
league_url = 'https://www.basketball-reference.com/leagues/NBA_{}.html'
schedule_url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'
leaders_url = 'https://www.basketball-reference.com/leagues/NBA_{}_leaders.html'
hof_url = 'https://en.wikipedia.org/wiki/List_of_players_in_the_Naismith_Memorial_Basketball_Hall_of_Fame'

#list for validation of users input
team_names = ['BOS', 'ATL', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 
              'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'BKN', 'OKC', 'ORL', 
              'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTH', 'WAS']
years = list(range(2003,datetime.date.today().year+1))
months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']

#main function
def main():
    hof_list = []
    get_hof(hof_list)
    choice = 1
    figlet.setFont(font = 'doom')
    print(figlet.renderText("Welcome  to  my  NBA  webscraper!"))
    while 0 < choice < 8:
        print("Chose what you want to know: ")
        print("1.League leaders\n2.Standings\n3.Team roster\n4.Team information\n5.Player stats\n6.League schedule\n7.Exit")
        choice = int(input("Select: "))
        match choice:
            case 1:
                year = int(input("Which year (2003-2025)?: "))
                if year in years:
                    find_leaders(year)
                else:
                    print("Invalid year!\n")
                    continue
            case 2:
                year = int(input("Which year (2003-2025)?: "))
                if year in years:
                    find_league_stands(year)
                else:
                    print("Invalid year!\n")
                    continue
            case 3:
                team = input("Type team abbreviation(example: Golden State Warriors = GSW): ")
                year = int(input("Which year (2003-2025)?: "))
                if (team in team_names) and (year in years):
                    get_team_roster(team, year)
                else:
                    print("Invalid team abbreviation or year!")
                    continue
            case 4:
                team = input("Type team abbreviation(example: Golden State Warriors = GSW): ")
                year = int(input("Which year (2003-2025)?: "))
                if (team in team_names) and (year in years):
                    team_inf(team, year)
                else:
                    print("Invalid team abbreviation or year!")
                    continue
            case 5:
                name = input("Player name: ")
                year = int(input("Which year (2003-2025)?: "))
                if name in hof_list:
                    name = name + '*'
                if year in years:
                    find_player_stats(year, name)
            case 6:
                year = int(input("Which year (2003-2025)?: "))
                month = input("Which month (october - april): ")
                if (year in years) and (month in months):
                    find_league_games(year, month)
            case _:
                print(figlet.renderText("Exiting the program..."))
                break
    driver.quit()

#gets (with selenium) html file from points per game section of website and returns it
def get_player_stats(year):
    url = p_s_url.format(year)
    driver.get(url)
    driver.execute_script("window.scroll(1,10000)")
    time.sleep(2)
    html = driver.page_source
    return html

#searches for a table with statistics from an html file and makes a dataframe, with pandas library, in which you can search for information
#hall of famers got the * with their name so functions checks if player was inducted 
def find_player_stats(year, name):
    try:
        html = get_player_stats(year)
        soup = BeautifulSoup(html, "html.parser")
        soup.find("tr", class_="thead").decompose()
        pgs_table = soup.find(id="per_game_stats")
        pgs = pd.read_html(StringIO(str(pgs_table)))
        df = pgs[0]
        print(df[df['Player'] == name])
    except:
        print("Invalid player name or year he didn't play!")

#gets (with selenium) html file from team page and returns it
def get_team_stats(team, year):
    url = team_url.format(team, year)
    driver.get(url)
    driver.execute_script("window.scroll(1,10000)")
    time.sleep(2)
    html = driver.page_source
    return html

#given html file, its searching for a table witch certain id, and making it into list of dataframes (with pandas library) sorted by jersey number
def get_team_roster(team, year):
    html = get_team_stats(team, year)
    soup = BeautifulSoup(html, 'html.parser')
    roster_table = soup.find(id = "roster")
    roster = pd.read_html(StringIO(str(roster_table)))[0]
    print(f"{roster.sort_values(by = ['No.'])}\n")

#with the same html as previous function, looks for a fragment containing basic information about the team
def team_inf(team, year):
    html = get_team_stats(team, year)
    soup = BeautifulSoup(html, "html.parser")
    soup.find('div', class_ = "prevnext").decompose()
    inf_tables = soup.find('div', attrs={'data-template' : 'Partials/Teams/Summary'})
    paragraphs = inf_tables.find_all('p')
    print("\n")
    for p in paragraphs:
        text = p.get_text().strip()
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        print(f"{text}")
        print("--------------------")


#gets (with selenium) html file from standings section of website and returns it
def get_league_stands(year):
    url = league_url.format(year)
    driver.get(url)
    driver.execute_script("window.scroll(1,10000)")
    time.sleep(2)
    html = driver.page_source
    return html

#some of the years included to be available doesnt have league standings, but always have division standing
#so function: decomposes theads, searches for table with certains id and prints it sorted by wins

def find_league_stands(year):
    html = get_league_stands(year)
    soup = BeautifulSoup(html, 'html.parser')
    theads = soup.find_all('tr', class_='thead')
    for thead in theads:
        thead.decompose()
    team_table_E = soup.find(id="divs_standings_E")
    east_records= pd.read_html(StringIO(str(team_table_E)))[0]
    team_table_W = soup.find(id="divs_standings_W")
    west_records = pd.read_html(StringIO(str(team_table_W)))[0]
    print(f"East:\n{east_records.sort_values(by = ['W'], ascending=False)}\nWest:\n{west_records.sort_values(by = ['W'], ascending=False)}\n")

#gets (with selenium) html file from schedule section of website and returns it
def get_league_games(year, month):
    url = schedule_url.format(year, month)
    driver.get(url)
    driver.execute_script("window.scroll(1,10000)")
    time.sleep(2)
    html = driver.page_source
    return html

#with given html file fuctions is decomposing thead, searching for table with certain id, and with pandas printing it as Dataframe
def find_league_games(year, month):
    html = get_league_games(year, month)
    soup = BeautifulSoup(html, 'html.parser')
    soup.find("tr", class_="thead").decompose()
    games_table = soup.find(id='schedule')
    pd.set_option('display.max_rows', None)
    games = pd.read_html(StringIO(str(games_table)))
    print(games[0])

#gets (with selenium) html file from stats leaders section of website and returns it
def get_leaders(year):
    url = leaders_url.format(year)
    driver.get(url)
    driver.execute_script("window.scroll(1,10000)")
    time.sleep(2)
    return driver.page_source

#given the html file searches of tables with certain id and prints top3 in (per game): points, assists, rebounds, blocks and win shares
def find_leaders(year):
    html = get_leaders(year)
    soup = BeautifulSoup(html, 'html.parser')
    ppg_table = soup.find('div', id = "leaders_pts_per_g")
    ppg = pd.read_html(StringIO(str(ppg_table)))
    apg_table = soup.find('div', id = "leaders_ast_per_g")
    apg = pd.read_html(StringIO(str(apg_table)))
    rpg_table = soup.find('div', id = "leaders_trb_per_g")
    rpg = pd.read_html(StringIO(str(rpg_table)))
    bpg_table = soup.find('div', id = "leaders_blk_per_g")
    bpg = pd.read_html(StringIO(str(bpg_table)))
    ws_table = soup.find('div', id = "leaders_ws")
    ws = pd.read_html(StringIO(str(ws_table)))
    print(f"\nPoints per game Top 3:\n{ppg[0].head(3)}\n")
    print(f"Assists per game Top 3:\n{apg[0].head(3)}\n")
    print(f"Rebounds per game Top 3:\n{rpg[0].head(3)}\n")
    print(f"Blocks per game Top 3:\n{bpg[0].head(3)}\n")
    print(f"Win shares Top 3:\n{ws[0].head(3)}\n")

#gets hall of fame players name from wikipedia page to validate searching for inductees in find_player_stats function
def get_hof(hof_list):
    html = (requests.get(hof_url)).text
    soup = BeautifulSoup(html, 'html.parser')
    hof_names = (soup.find_all('span', class_ = 'fn'))
    for hof in hof_names:
        hof_list.append(hof.text)

if __name__ == "__main__":
    main()

