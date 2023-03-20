import datetime
from zoneinfo import ZoneInfo

import discord
import requests
from discord.ext import tasks, commands
import random

from Database import Database

from Token import riot_api_key

tiers = {
    "IRON": 1,
    "BRONZE": 2,
    "SILVER": 3,
    "GOLD": 4,
    "PLATINUM": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9
}
ranks = {
    "IV": 1,
    "III": 2,
    "II": 3,
    "I": 4,
}

colors = [0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F, 0x800000, 0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585, 0xFFB6C1, 0x00CED1]


# https://ddragon.leagueoflegends.com/api/versions.json -> take first array
req = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
last_icon_version = req.json()[0]

db = Database()

class CustomHelpCommand(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Aide", color=0x00ff00)
        embed.add_field(name="/bug <message>", value="Alerte l'administrateur d'un(e) potentiel(le) problème/demande", inline=False)
        embed.add_field(name="/addjoueur <summonername>", value="Ajoute un joueur à la base de données", inline=False)
        embed.add_field(name="/classement", value="Affiche le classement du serveur", inline=False)
        embed.add_field(name="/profil <summonername>", value="Affiche le profil du joueur", inline=False)
        embed.add_field(name="/profildiscord <membre>", value="Affiche le profil du joueur", inline=False)
        embed.add_field(name="/help", value="Affiche l'aide", inline=False)
        await self.get_destination().send(embed=embed)



def displayInfo(player):
    temp = "Le joueur " + player.get("summonername") + " est classé " + str(player.get("tier")) + " " + \
           str(player.get("rank")) + " avec " + str(player.get("lps")) + " LPs."
    if player.get("enBo") == 1:
        x = player.get("progress").replace('W', ":white_check_mark: ")\
            .replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
        temp += "\nLe joueur est actuellement en BO : " + x
    return temp


def createPlayer(acc, rank):
    for typegames in rank:
        if typegames.get('queueType') == "RANKED_SOLO_5x5":
            if typegames.get('miniSeries') is not None:
                prog = typegames.get('miniSeries')
                progress = prog.get('progress')
                enBo = True
            else:
                progress = ""
                enBo = False
            rc = db.addJoueur(acc.get('id'), acc.get('name'), typegames.get('tier'), typegames.get('rank'), acc.get('profileIconId'),
                              typegames.get('leaguePoints'), enBo, progress)
            # db.AddClassemen0t(acc.get('id'))
            return rc


def addPlayer(summonername):
    urlSummoners = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonername + \
                   '?api_key=' + riot_api_key
    r = requests.get(urlSummoners)
    if r.status_code != 200:
        print("Code erreur : " + str(r.status_code))
        print("Erreur API Riot.")
        return None
    account = r.json()
    urlRanks = 'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + account.get('id') + \
               '?api_key=' + riot_api_key
    r = requests.get(urlRanks)
    ranking = r.json()
    if r.status_code != 200:
        print("Erreur API Riot.")
        return None
    nbr = createPlayer(account, ranking)
    return nbr


def check_rang(player, guild='0'):
    urlRanks = 'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + player[0] + \
               '?api_key=' + riot_api_key
    r = requests.get(urlRanks)
    ranking = r.json()
    if r.status_code != 200:
        print("Code erreur : " + str(r.status_code))
        print("Erreur API Riot.")
        return None
    for typequeue in ranking:
        if typequeue.get('queueType') == 'RANKED_SOLO_5x5':
            ret = ""
            eloactuel = {
                "summonername": player[2],
                "tier": player[3],
                "rank": player[4],
                "lps": player[5],
                "enBo": player[6],
                "progress": player[7]
            }
            newelo = {
                "summonername": typequeue.get('summonerName'),
                "tier": typequeue.get('tier'),
                "rank": typequeue.get('rank'),
                "lps": typequeue.get('leaguePoints'),
                "eb": 0,
                "prog": None
            }
            if typequeue.get('miniSeries') is not None:
                eloactuel["enBo"] = True
                newelo["enBo"] = 1
                miniS = typequeue.get('miniSeries')
                progress = miniS.get('progress')
                newelo["progress"] = progress
                if progress != eloactuel["progress"]:
                    db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'),
                                    typequeue.get('rank'),
                                    typequeue.get('leaguePoints'), eloactuel.get("enBo"), progress)
                    tab_progress = list(filter('N'.__ne__, progress))
                    if len(tab_progress) != 0 and tab_progress[len(tab_progress) - 1] == 'W':
                        db.UpdateWinClassement(player[0])
                    return [ret, newelo]
            else:
                eloactuel["enBo"] = False
            if typequeue.get('tier') == eloactuel.get("tier") and typequeue.get('rank') == eloactuel.get("rank") and \
                    typequeue.get('leaguePoints') == eloactuel.get("lps"):
                return ["RAS", newelo]
            
            # TypeError: '<' not supported between instances of 'int' and 'NoneType'
            if typequeue.get('tier') != eloactuel.get("tier") \
                    and tiers.get(typequeue.get('tier')) < tiers.get(eloactuel.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a derank de " + eloactuel.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                return [ret, newelo, 0]
            if typequeue.get('tier') != eloactuel.get("tier") \
                    and tiers.get(typequeue.get('tier')) > tiers.get(eloactuel.get("tier")):
                ret += str(typequeue.get('summonerName')) + " a rank up de " + eloactuel.get('tier') + " à " \
                       + typequeue.get('tier')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                db.UpdateWinClassement(player[0])
                return [ret, newelo, 1]

            if typequeue.get('rank') != eloactuel.get("rank") \
                    and ranks.get(typequeue.get('rank')) < ranks.get(eloactuel.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est descendu de " + eloactuel.get("tier") + ' ' + \
                       eloactuel.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                return [ret, newelo, 0]
            if typequeue.get('rank') != eloactuel.get("rank") \
                    and ranks.get(typequeue.get('rank')) > ranks.get(eloactuel.get("rank")):
                ret += str(typequeue.get('summonerName')) + " est monté de " + eloactuel.get("tier") + ' ' + \
                       eloactuel.get("rank") \
                       + " à " + typequeue.get('tier') + ' ' + typequeue.get('rank')
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                db.UpdateWinClassement(player[0])
                return [ret, newelo, 1]

            if typequeue.get('leaguePoints') != eloactuel.get("lps") and typequeue.get('leaguePoints') < \
                    eloactuel.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a perdu -" + \
                       str(eloactuel.get("lps") - typequeue.get('leaguePoints')) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                return [ret, newelo,0]
            if typequeue.get('leaguePoints') != eloactuel.get("lps") and typequeue.get('leaguePoints') > \
                    eloactuel.get("lps"):
                ret += str(typequeue.get('summonerName')) + " a gagné +" + \
                       str(typequeue.get('leaguePoints') - eloactuel.get("lps")) + " LPs"
                db.updateJoueur(player[0], typequeue.get('summonerName'), typequeue.get('tier'), typequeue.get('rank'),
                                typequeue.get('leaguePoints'), eloactuel.get("enBo"), eloactuel.get("progress"))
                db.UpdateWinClassement(player[0])
                return [ret, newelo,1]
            
def add_history( EncryptedID, date_time, summoner_names, result, lp_change):
    # def addGameHistory(self, EncryptedID, date_time, summoner_names, result, lp_change):
    db = Database()
    db.addGameHistory(EncryptedID=EncryptedID, date_time=date_time, summoner_names=summoner_names, result=result,
                      lp_change=lp_change)


def get_history(EncryptedID):
    db = Database()
    return db.getGameHistory(EncryptedID)

def get_random_color():
    # from the list of colors, get a random color
    return random.choice(colors)