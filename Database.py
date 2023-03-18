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

    def InitializeServer(self, guildid, cim, rtp):
        request = "UPDATE serveurs SET channelIdMessage=%s, roleToPing=%s " \
                  "WHERE guildId=%s"
        params = [cim, rtp, guildid]
        self.cursor.execute(request, params)
        self.db.commit()

    def addServeur(self, guildid, guildname, cim, rtp):
        request = "INSERT INTO serveurs (guildID, guildName, channelIdMessage, roleToPing) "\
                  "VALUES (%s, %s, %s, %s)"
        params = [guildid, guildname, cim, rtp]
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

    def removeAllJoueurs(self, guildid):
        r1 = "SELECT * FROM joueurs;"
        self.cursor.execute(r1)
        j = self.cursor.fetchall()
        enc_ids = []
        for jr in j:
            enc_ids.append(jr[0])
        dup = [x for i, x in enumerate(enc_ids) if x in enc_ids[:i]]
        del_list = []
        for joueur in j:
            if joueur[0] not in dup and joueur[7] == guildid:
                del_list.append(joueur[0])
        if del_list:
            r2 = "DELETE FROM classement WHERE joueur IN ({});".format(", ".join(del_list))
            self.cursor.execute(r2)
            self.db.commit()
        r3 = "DELETE FROM joueurs WHERE guildID = %s"
        p2 = [guildid]
        self.cursor.execute(r3, p2)
        self.db.commit()

    def addJoueur(self, encryptedid, summonername, tier, rank, lps, eb, prog, guildid, member_id):
        request = "INSERT INTO joueurs (EncryptedID, SummonerName, Tier, `Rank`, leaguePoints, enBO, Progress, " \
                "guildID, memberID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = [encryptedid, summonername, tier, rank, lps, eb, prog, guildid, member_id]
        try:
            self.cursor.execute(request, params)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.errors.IntegrityError:
            return 2


    def GetJoueurFromMemberId(self, memberID):
        request = "SELECT * FROM joueurs WHERE memberID = %s"
        print(memberID)
        params = [memberID]
        self.cursor.execute(request, params)
        return self.cursor.rowcount, self.cursor.fetchall()

    def RemoveJoueur(self, guildid, member_id):
        request = "DELETE FROM joueurs WHERE guildID=%s AND memberID=%s"
        params = [guildid, member_id]
        self.cursor.execute(request, params)
        self.db.commit()

    def updateJoueur(self, playerid, summonername, tier, rank, lps, eb, prog):
        request = "UPDATE joueurs SET SummonerName=%s, Tier=%s, Rank=%s, leaguePoints=%s, enBO=%s, Progress=%s"\
                  " WHERE EncryptedID=%s"
        params = [summonername, tier, rank, lps, eb, prog, playerid]
        self.cursor.execute(request, params)
        self.db.commit()

    def recoverAllGuilds(self):
        request = "SELECT * FROM serveurs WHERE channelIdMessage != 0"
        self.cursor.execute(request)
        results = self.cursor.fetchall()
        return results

    def GetJoueursOfGuild(self, guildid):
        request = "SELECT * FROM joueurs WHERE guildID=" + str(guildid) + ";"
        self.cursor.execute(request)
        resultats = self.cursor.fetchall()
        return resultats

    def GetPlayerInfo(self, guildid, summonername):
        request = "SELECT * FROM joueurs WHERE guildID=%s and SummonerName=%s"
        params = [guildid, summonername]
        self.cursor.execute(request, params)
        result = self.cursor.fetchone()
        return result

    def GetPlayerInfoDiscord(self, guildid, discordid):
        request = "SELECT * FROM joueurs WHERE guildID=%s and memberID=%s"
        params = [guildid, discordid]
        self.cursor.execute(request, params)
        result = self.cursor.fetchone()
        return result

    def UpdatePlayerRecover(self):
        request = "SELECT * FROM joueurs, serveurs WHERE joueurs.guildID = serveurs.guildID;"
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

    def GetClassement(self, guildid):
        request = "SELECT joueurs.SummonerName, joueurs.memberID, classement.nbrWin, serveurs.channelIdMessage " \
                  "FROM classement INNER JOIN joueurs ON joueurs.EncryptedID = classement.joueur INNER JOIN serveurs " \
                  "ON serveurs.guildID = joueurs.guildID WHERE joueurs.guildID = %s ORDER BY classement.nbrWin DESC" \
                  " LIMIT 3;"
        params = [guildid]
        self.cursor.execute(request, params)
        result = self.cursor.fetchall()
        return result
