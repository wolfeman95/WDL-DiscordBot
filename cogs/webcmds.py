from datetime import datetime
import re
from discord.ext import commands
import bs4 as bs
import pandas as pd
import aiohttp

http = aiohttp.ClientSession()

class Web():
    """Web holds all the commands relating to web-stuff.  WDL Standings and gametimes mostly."""
    def __init__(self, bot):
        self.bot = bot

    async def noGamesToday(self):
        await self.bot.say("No games today!")

    @commands.command()
    async def standings(self):
        """!standings - returns current WDL season standings."""
        wdl_standings = pd.read_html("http://doomleague.org", index_col=0)
        standings_table = wdl_standings[0][["PTS", "PF", "PA"]]
        await self.bot.say("```WDL Season 7 Standings\n\n{}```".format(str(standings_table)))

    @commands.command()
    async def gametime(self):
        """!gametime - returns a list of gametimes."""
        gametime_regex = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEST"
        playoff_gametime_regex = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEDT"

        resp = await http.get("http://doomleague.org/")
        sauce = await resp.text()
        soup = bs.BeautifulSoup(sauce, "lxml")
        game_times = soup.find_all(text=re.compile(gametime_regex))
        game_times_playoffs = soup.find_all(text=re.compile(playoff_gametime_regex))

        if game_times or game_times_playoffs:
            await self.bot.say("{} , {}".format(game_times, game_times_playoffs))


    @commands.command()
    async def today(self):
        """!today - returns matchup and time if there is a game today."""
        #gametime regexs from wdl.org
        gametime_str = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEST"
        playoff_gametime_re = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEDT"
        team_str = r"([\w]+)+\s\[...\]"
        playoff_team_re = r"#[0-9]\s[\w\s]+\s\[...\]\s\(MAP[0-9]+\)"

        #bs4 stuff
        resp = await http.get("http://doomleague.org/")
        sauce = await resp.text()
        soup = bs.BeautifulSoup(sauce, "lxml")
        game_times = soup.find_all(text=re.compile(gametime_str))
        game_times_playoffs = soup.find_all(text=re.compile(playoff_gametime_re))

        #lists of regexs
        matchups = soup.find_all(text=re.compile(team_str))
        playoff_matchups = soup.find_all(text=re.compile(playoff_team_re))
        date_objects = []
        date_objects_playoffs = []
        tday = datetime.today()

        number_of_games_on_site = 0
        number_of_playoff_games_on_site = 0
        is_game_today = False

        if game_times:
            for regexs in game_times:
                date_objects.append(datetime.strptime(regexs, "Gametime: %A, %b %d @ %I:%M%p EST"))

            number_of_games_on_site = len(date_objects)

            for obj in date_objects:
                if obj.day == tday.day and obj.month == tday.month:
                    is_game_today = True
                    await self.bot.say("**{} vs {}** - today {}/{} at {}:{}"
                                       "EST!".format(matchups[(date_objects.index(obj) * 2)],
                                                     matchups[(date_objects.index(obj) * 2) + 1],
                                                     obj.month,
                                                     obj.day,
                                                     obj.hour,
                                                     obj.minute))

        print("{} regular season games on file".format(number_of_games_on_site))

        if game_times_playoffs:

            for regexs in game_times_playoffs:
                date_objects_playoffs.append(datetime.strptime(regexs, "Gametime: %A, %b %d @ %I:%M%p EDT"))

            number_of_playoff_games_on_site = len(date_objects_playoffs)

            for obj in date_objects_playoffs:
                if obj.day == tday.day and obj.month == tday.month and tday.hour < obj.hour:
                    is_game_today = True
                    await self.bot.say("**{} @ {}** - today {}/{} at {}:{}"
                                       "EST!".format(playoff_matchups[(date_objects_playoffs.index(obj) * 2)],
                                                     playoff_matchups[(date_objects_playoffs.index(obj) * 2) + 1],
                                                     obj.month,
                                                     obj.day,
                                                     obj.hour,
                                                     obj.minute))


        print("{} playoff games on file".format(number_of_playoff_games_on_site))

        if not is_game_today:
            await self.bot.say("No games today.")
        else:
            pass

    @commands.command()
    async def lastgame(self):
        """Returns the most recent game that took place"""
        # gametime regexs from wdl.org
        gametime_str = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEST"
        playoff_gametime_re = r"Gametime:\s[\w]+,\s[\w]{3}\s[0-9]+\s@\s[0-9]+:[0-9][0-9]PM\sEDT"
        team_str = r"([\w]+)+\s\[...\]"
        playoff_team_re = r"#[0-9]\s[\w\s]+\s\[...\]\s\(MAP[0-9]+\)"

        # bs4 stuff
        resp = await http.get("http://doomleague.org/")
        sauce = await resp.text()
        soup = bs.BeautifulSoup(sauce, "lxml")
        game_times = soup.find_all(text=re.compile(gametime_str))
        game_times_playoffs = soup.find_all(text=re.compile(playoff_gametime_re))

        # lists of regexs
        matchups = soup.find_all(text=re.compile(team_str))
        playoff_matchups = soup.find_all(text=re.compile(playoff_team_re))
        date_objects = []
        date_objects_playoffs = []
        tday = datetime.today()

        no_documented_games = False

        if game_times:
            for regexs in game_times:
                date_objects.append(datetime.strptime(regexs, "Gametime: %A, %b %d @ %I:%M%p EST"))
        else:
            no_documented_games = True
        if game_times_playoffs:
            for regexs in game_times_playoffs:
                date_objects_playoffs.append(datetime.strptime(regexs, "Gametime: %A, %b %d @ %I:%M%p EDT"))
                no_documented_games = False

        if no_documented_games:
            await self.bot.say("No games on record..")
        else:
            await self.bot.say("Last game took place {}".format(date_objects_playoffs[-1].strftime("%B-%d")))

def setup(bot):
    bot.add_cog(Web(bot))
