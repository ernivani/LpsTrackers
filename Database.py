import mysql.connector

class Database(object):
    db = None
    cursor = None

    def __init__(self):
        try:
            self.db = mysql.connector.connect(host='localhost',
                                              user='root',
                                              password='ernicani',
                                              database='LpsTracker')
            self.cursor = self.db.cursor(buffered=True)
        except Exception as e:
            print(e)

    def InitializeServer(self, guildid, cim):
        request = "UPDATE serveurs SET channelIdMessage=%s " \
                "WHERE guildID=%s"
        params = [cim, guildid]
        self.cursor.execute(request, params)
        self.db.commit()


    def addServeur(self, guildid, guildname, cim):
        request = "INSERT INTO serveurs (guildID, guildName, channelIdMessage) "\
                  "VALUES (%s, %s, %s);"
        params = [guildid, guildname, cim]
        # print the SQL query
        print(request , params)
        self.cursor.execute(request, params)
        self.db.commit()

    def removeServeur(self, guildid):
        request = "DELETE FROM serveurs WHERE guildID=%s ;"
        params = [guildid]
        self.cursor.execute(request, params)
        self.db.commit()

    def getServeur(self, guildid):
        request = "SELECT * FROM serveurs WHERE guildID=%s"
        params = [guildid]
        self.cursor.execute(request, params)
        return self.cursor.fetchone()
    
    def getAllChannels(self):
        request = "SELECT channelIdMessage FROM serveurs WHERE channelIdMessage != 0"
        self.cursor.execute(request)
        return self.cursor.fetchall()

    def addJoueur(self, encryptedid, summonername, tier, rank, lps, eb, prog, member_id):
        request = "INSERT INTO joueurs (EncryptedID, SummonerName, Tier, `Rank`, leaguePoints, enBO, Progress, " \
                " memberID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = [encryptedid, summonername, tier, rank, lps, eb, prog, member_id]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.errors.IntegrityError:
            return 2


    def GetJoueurFromMemberId(self, memberID):
        request = "SELECT * FROM joueurs WHERE memberID = %s"
        params = [memberID]
        self.cursor.execute(request, params)
        return self.cursor.rowcount, self.cursor.fetchall()

    def RemoveJoueur(self,  member_id):
        request = "DELETE FROM joueurs WHERE memberID=%s"
        params = [member_id]
        self.cursor.execute(request, params)
        self.db.commit()

    def updateJoueur(self, playerid, summonername, tier, rank, lps, eb, prog):
        request = "UPDATE joueurs SET SummonerName=%s, Tier=%s, `Rank`=%s, leaguePoints=%s, enBO=%s, Progress=%s"\
             " WHERE EncryptedID=%s"
        params = [summonername, tier, rank, lps, eb, prog, playerid]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
        except Exception as e:
            print("An error occurred while updating the player record: ", e)


    def recoverAll(self):
        request = "SELECT * FROM serveurs WHERE channelIdMessage != 0"
        self.cursor.execute(request)
        results = self.cursor.fetchall()
        return results


    def GetPlayerInfo(self, summonername):
        request = "SELECT * FROM joueurs WHERE SummonerName=%s"
        params = [summonername]
        self.cursor.execute(request, params)
        result = self.cursor.fetchone()
        return result

    def GetPlayerInfoDiscord(self, member_id):
        request = "SELECT * FROM joueurs WHERE memberID=%s"
        params = [member_id]
        self.cursor.execute(request, params)
        result = self.cursor.fetchone()
        print(result)
        return result

    def UpdatePlayerRecover(self):
        request = "SELECT * FROM joueurs;"
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return result

    def AddClassement(self, encryptedid):
        request = "INSERT INTO classement VALUES (%s, %s)"
        params = [encryptedid, 0]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.errors.IntegrityError:
            return 2

    def DeleteClassement(self, EncryptedID):
        request = "DELETE FROM classement WHERE joueur = %s"
        params = [EncryptedID]
        self.cursor.execute(request, params)
        self.db.commit()

    def UpdateWinClassement(self, encryptedid):
        request = "UPDATE classement SET nbrWin = nbrWin + 1 WHERE joueur = %s"
        params = [encryptedid]
        self.cursor.execute(request, params)
        self.db.commit()
        return self.cursor.rowcount

    def ResetClassement(self):
        request = "UPDATE classement SET nbrWin = 0"
        self.cursor.execute(request)
        self.db.commit()

    def GetClassement(self):
        request = "SELECT DISTINCT joueurs.SummonerName, joueurs.memberID, classement.nbrWin " \
                  "FROM classement INNER JOIN joueurs ON joueurs.EncryptedID = classement.joueur INNER JOIN serveurs "\
                    " ORDER BY classement.nbrWin DESC "
        self.cursor.execute(request)
        result = self.cursor.fetchall()
        return result

    def addGameHistory(self, EncryptedID, date_time, summoner_names, result, lp_change):
        request = "INSERT INTO game_history (EncryptedID, date_time, summoner_names, result, lp_change) VALUES (%s, %s, %s, %s, %s)"
        params = [EncryptedID, date_time, summoner_names, result, lp_change]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.errors.IntegrityError:
            return 2
        
    def getGameHistory(self, EncryptedID):
        request = "SELECT * FROM game_history WHERE EncryptedID = %s ORDER BY date_time DESC LIMIT 10"
        params = [EncryptedID]
        self.cursor.execute(request, params)
        result = self.cursor.fetchall()
        return result
    