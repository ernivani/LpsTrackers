import datetime
from zoneinfo import ZoneInfo

import discord
import requests
from discord.ext import tasks, commands

from Database import Database

from Token import TOKEN, riot_api_key 

compteur = 0
db = Database()
admin_id = [486268235017093130]
server_id = 1077666645176225893


intents = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=intents)

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

client.help_command = CustomHelpCommand()


def displayInfo(player):
    temp = "Le joueur " + player.get("summonername") + " est classé " + str(player.get("tier")) + " " + \
           str(player.get("rank")) + " avec " + str(player.get("lps")) + " LPs."
    if player.get("enBo") == 1:
        x = player.get("progress").replace('W', ":white_check_mark: ")\
            .replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
        temp += "\nLe joueur est actuellement en BO : " + x
    return temp


def createPlayer(acc, rank, member_id):
    for typegames in rank:
        if typegames.get('queueType') == "RANKED_SOLO_5x5":
            if typegames.get('miniSeries') is not None:
                prog = typegames.get('miniSeries')
                progress = prog.get('progress')
                enBo = True
            else:
                progress = ""
                enBo = False
            rc = db.addJoueur(acc.get('id'), acc.get('name'), typegames.get('tier'), typegames.get('rank'),
                              typegames.get('leaguePoints'), enBo, progress, member_id)
            db.AddClassement(acc.get('id'))
            return rc


def addPlayer(summonername, member_id):
    urlSummoners = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summonername + \
                   '?api_key=' + riot_api_key
    print(urlSummoners)
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
    nbr = createPlayer(account, ranking, member_id)
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
                "summonername": player[1],
                "tier": player[2],
                "rank": player[3],
                "lps": player[4],
                "enBo": player[5],
                "progress": player[6]
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


@client.event
async def on_ready():
    print('Connecté en tant que')
    print(client.user.name)
    print(client.user.id)
    print('-------')
    print(f'{client.user} is connected to the following guilds:\n')
    for guild in client.guilds:
        print(
            f'{guild.name}(id: {guild.id})'
        )
        if db.getServeur(guild.id) is None:
            db.addServeur(guild.id, guild.name, 0)
            
    print("Synchro du tree...")
    await client.tree.sync()
    await client.wait_until_ready()
    print("Chargement de l'activité...")
    stream = discord.Streaming(name="League of Legends", url="https://www.twitch.tv/riotgames")
    await client.change_presence(activity=stream, status=discord.Status.online)
    
    print("Chargement des tâches...")
    on_update.start()



@client.event
async def on_guild_join(guild):
    print("GuildAdd : le bot a été ajouté sur un serveur")
    db.addServeur(guild.id, guild.name, 0)
    return


@client.event
async def on_guild_remove(guild):
    print("GuildRemove : un serveur a supprimé le bot")
    db.removeServeur(guild.id)
    return


@client.event
async def on_member_remove(member):
    print("MemberRemove : un joueur a quitté un serveur qui a entraîné son retrait de la BDD")
    rowCount, res = db.GetJoueurFromMemberId(member.id)
    if rowCount == 1:
        db.RemoveJoueur(member.guild.id, member.id)
        db.DeleteClassement(res[0][0])
    elif rowCount > 1:
        db.RemoveJoueur(member.guild.id, member.id)
    return


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    await client.process_commands(message)

@client.tree.command(name="initialize", description="Initialise un nouveau serveur")
async def initialize(ints, channelmessage: discord.TextChannel,
                     roleaping: discord.Role = None):
    print("Initialisation : une initialisation a été demandée")
    try:
        msg = "Message test. Si vous voyez ce message, cela signifie que le bot a l'autorisation d'écrire dans le " \
              "channel. Vous pouvez le supprimer dès la fin de l'initialisation."
        await channelmessage.send(msg)
    except discord.errors.Forbidden:
        msg = "Le bot n'a pas l'autorisation d'écrire dans le channel : " + channelmessage.name + \
              ". Veuillez changer de channel ou accorder les autorisations avant de recommencer."
        await ints.response.send_message(msg)
        return
    else:
        if not roleaping:
            roleaping = 0
            db.InitializeServer( ints.guild.id, channelmessage.id)
        else:
            db.InitializeServer( ints.guild.id, channelmessage.id)
        await ints.response.send_message("Le serveur a bien été initialisé")

@client.tree.command(name="addjoueur", description="S'ajouter dans la liste des joueurs")
async def addJoueur(ints, nomjoueur: str):
    print("Addjoueur : une demande d'ajout a été envoyée")
    ret = addPlayer(nomjoueur, ints.user.id)
    if ret is None:
        msg = "Erreur lors de l'ajout du joueur. Veuillez vérifier qu'il existe bien, qu'il est niveau 30 et qu'il" \
              " a fini ses games de placements."
        await ints.response.send_message(msg)
    elif ret == 1:
        await ints.response.send_message("Vous avez bien été ajouté à la liste.")
    elif ret == 2:
        await ints.response.send_message("Vous êtes déjà dans la liste du Bot.")
    else:
        print("Erreur lors de l'ajout.")



@client.tree.command(name="alert", description="Alerte tous les utilisateurs du bot")
async def alertGuilds(ints, message: str):
    if ints.user.id not in admin_id:
        await ints.response.send_message("Seul l'administrateur peut utiliser cette commande")
        return
    await ints.response.defer()
    for g in db.recoverAll():
        channel = client.get_channel(int(g[3]))
        try:
            await channel.send("Message de l'admin : \n>>> " + message)
        except Exception as e:
            print(e)
    print("Alert : une alerte a été envoyée aux serveurs")
    await ints.followup.send("L'alerte a bien été envoyée")

@client.tree.command(name="bug", description="Alerte l'administrateur d'un(e) potentiel(le) problème/demande")
async def alert_admin(ints, message: str):
    await ints.response.defer()
    atlas = await client.fetch_user(admin_id[0])
    ret = "<@" + str(ints.user.id) + "> vous a envoyé un message : \n\n" + message
    await atlas.send(ret)
    await ints.followup.send("Votre message a bien été envoyé. Vous serez recontacté sous peu."
                             " Merci de ne pas spam la commande")

@client.tree.command(name="classement", description="Affiche le classement du serveur")
async def classement(ints):
    await ints.response.defer()
    print("Classement : un classement a été demandé à la BDD")
    res = db.GetClassement()

    if not res:
        # Si le classement est vide, on renvoie un message d'erreur
        await ints.followup.send("Le classement est vide")
    else:
        # Sinon, on crée un embed avec les 10 premiers joueurs du classement
        embed = discord.Embed(title="Classement", color=0x00ff00)
        for i in range(10):
            if i < len(res):
                player_name = res[i][0]
                player_wins = res[i][2]
                embed.add_field(name=f"{i + 1}. {player_name}", value=f"{player_wins} Wins", inline=False)

        await ints.followup.send(embed=embed)



@client.tree.command(name="profil", description="Affiche le profil d'un joueur")
async def profil(ints, summonername: str = None):
    db = Database()
    await ints.response.defer()

    # Si le nom d'invocateur n'est pas précisé, on prend celui enregistré dans la base de données pour l'utilisateur
    if summonername is None:
        user_id = ints.user.id
        summonername = db.GetPlayerInfoDiscord(user_id)
        if summonername is None:
            await ints.followup.send("Vous n'avez pas de profil enregistré. Veuillez en créer un avec la commande /addjoueur")
            return
        
        summonername = summonername[1]

    print("Profil : un profil a été demandé à la BDD")
    player_info = db.GetPlayerInfo( summonername)

    if not player_info:
        # Si le joueur n'existe pas dans la base de données, on renvoie un embed d'erreur
        embed = discord.Embed(title=f"Profil de {summonername}", color=0xff0000)
        embed.add_field(name="Rang", value="Joueur non trouvé dans notre base de données", inline=False)
    else:
        # Si le joueur existe, on crée un embed avec ses informations
        player_name = player_info[1]
        rank = f"{player_info[2]} {player_info[3]} avec {player_info[4]} LPs"
        embed = discord.Embed(title=f"Profil de {player_name}", color=0x00ff00)
        embed.add_field(name="Rang", value=rank, inline=False)

        # On ajoute les informations de la dernière série de parties classées
        if player_info[5] == 1:
            games_str = player_info[6].replace('W', ":white_check_mark: ").replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
            embed.add_field(name="BO", value=games_str, inline=False)

        # On ajoute l'historique des 10 dernières parties
        games = get_history(player_info[0])
        if games:
            games_str = "\n".join([f"{game[1]} : {'Victoire' if game[3] == '1' else 'Défaite'} avec {game[4]} LPs" for game in games])
            embed.add_field(name="Historique", value=games_str, inline=False)
        else:
            embed.add_field(name="Historique", value="Aucune partie trouvée", inline=False)

    await ints.followup.send(embed=embed)



@client.tree.command(name="profildiscord", description="Affiche le profil d'un joueur")
async def profil_discord(ints, membre: discord.Member = None):
    db = Database()
    await ints.response.defer()
    if membre is None:
        summonername = db.GetPlayerInfoDiscord( ints.user.id)[1]
        if summonername is None:
            await ints.followup.send("Vous n'avez pas de profil enregistré. Veuillez en créer un avec la commande /addjoueur")
            return
    else:
        summonername = db.GetPlayerInfoDiscord( membre.id)
        if summonername is None:
            await ints.followup.send("Ce joueur n'a pas de profil enregistré. Demandez lui de créer un profil avec la commande /addjoueur")
            return
        summonername = summonername[1]
    print("Profil : un profil a été demandé à la BDD")
    p = db.GetPlayerInfo( summonername)
    if not p:
        embed = discord.Embed(title=f"Profil de {summonername}", color=0xff0000)
        embed.add_field(name="Rang", value="Joueur non trouvé", inline=False)
    else:
        embed = discord.Embed(title=f"Profil de {p[1]}", color=0x00ff00)
        embed.add_field(name="Rang", value=f"{p[2]} {p[3]} avec {p[4]} LPs", inline=False)
        if p[5] == 1:
            x = p[6].replace('W', ":white_check_mark: ").replace('L', ":no_entry_sign: ").replace('N', ":clock3: ")
            embed.add_field(name="BO", value=x, inline=False)
    await ints.followup.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return # empêcher l'affichage de l'erreur CommandNotFound

@tasks.loop(minutes=3)
async def on_update():
    global compteur
    compteur += 1
    print("\nVérification n°" + str(compteur))
    for i in db.UpdatePlayerRecover():
        channels = db.getAllChannels()
        
        retour = check_rang(i)
        if retour is None:
            print("Erreur RIOT API.")
        elif retour[0] != "RAS":
            lpchange = int(retour[1]['lps'] -int(i[4]))
            add_history(EncryptedID=i[0], date_time=datetime.datetime.now(ZoneInfo("Europe/Paris")),
                        summoner_names=i[1], result=retour[2], lp_change=lpchange)
            retour[0] += "\n" + displayInfo(retour[1])
            try:
                for channel_id in channels:
                    channel = client.get_channel(int(channel_id[0]))
                    if channel is not None:
                        # await channel.send(retour[0])
                        embed = discord.Embed(title=f"Rang de {i[1]}", color=0x00ff00)
                        embed.add_field(name="Rang", value=retour[0], inline=False)
                        await channel.send(embed=embed)
                    else:
                        print("Error guild not found")
            except discord.errors.Forbidden:
                print("Error guild not found")


client.run(TOKEN)