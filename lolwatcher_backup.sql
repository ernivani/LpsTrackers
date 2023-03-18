-- MySQL dump 10.13  Distrib 8.0.32, for Linux (x86_64)
--
-- Host: localhost    Database: LolWatcher
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `classement`
--

DROP TABLE IF EXISTS `classement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classement` (
  `joueur` varchar(255) NOT NULL,
  `nbrWin` int NOT NULL,
  PRIMARY KEY (`joueur`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classement`
--

LOCK TABLES `classement` WRITE;
/*!40000 ALTER TABLE `classement` DISABLE KEYS */;
INSERT INTO `classement` VALUES ('CH-IK42wZjB1YxnpjhBzRn16DmzZVZV0GGbfx3jN2ifxGyUvBE1NqfaYwA',0),('ODy9Y80VThsdqB19nFAqD5hREe6wtAQJTBDdUXZLQjuPGFE',0),('Os52rJqQpxoc5Oj1ErsFjSteh1oeb3t_yf7f_ooTHMQVaxc',0);
/*!40000 ALTER TABLE `classement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `joueurs`
--

DROP TABLE IF EXISTS `joueurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `joueurs` (
  `EncryptedID` varchar(255) NOT NULL,
  `SummonerName` varchar(255) DEFAULT NULL,
  `Tier` varchar(255) DEFAULT NULL,
  `Rank` varchar(20) DEFAULT NULL,
  `leaguePoints` int DEFAULT NULL,
  `enBO` int DEFAULT NULL,
  `Progress` varchar(255) DEFAULT NULL,
  `guildID` varchar(255) DEFAULT NULL,
  `memberID` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`EncryptedID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `joueurs`
--

LOCK TABLES `joueurs` WRITE;
/*!40000 ALTER TABLE `joueurs` DISABLE KEYS */;
INSERT INTO `joueurs` VALUES ('CH-IK42wZjB1YxnpjhBzRn16DmzZVZV0GGbfx3jN2ifxGyUvBE1NqfaYwA','CAlTLŸN','BRONZE','II',1,0,'','1077666645176225893','486268235017093130'),('ODy9Y80VThsdqB19nFAqD5hREe6wtAQJTBDdUXZLQjuPGFE','Teemo Ukraine','PLATINUM','II',67,0,'','1077666645176225893','486268235017093130'),('Os52rJqQpxoc5Oj1ErsFjSteh1oeb3t_yf7f_ooTHMQVaxc','MrBarbax','BRONZE','IV',1,0,'','1077666645176225893','486268235017093130'),('Xv8W3OYlStc79TK4-hkdgj8DMMoZFuFV-sxS4Z0YP6T9Ml8H','UPDT ernicani','PLATINUM','III',57,0,'','1077666645176225893','486268235017093130');
/*!40000 ALTER TABLE `joueurs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serveurs`
--

DROP TABLE IF EXISTS `serveurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `serveurs` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guildID` varchar(30) NOT NULL,
  `guildName` varchar(30) NOT NULL,
  `channelIdMessage` varchar(30) NOT NULL,
  `roleToPing` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serveurs`
--

LOCK TABLES `serveurs` WRITE;
/*!40000 ALTER TABLE `serveurs` DISABLE KEYS */;
/*!40000 ALTER TABLE `serveurs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-18 20:10:38
