-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: eventhopia
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `active_users`
--

DROP TABLE IF EXISTS `active_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `active_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `login_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `active_users`
--

LOCK TABLES `active_users` WRITE;
/*!40000 ALTER TABLE `active_users` DISABLE KEYS */;
INSERT INTO `active_users` VALUES (94,'testuser','2026-06-13 12:44:05'),(95,'Atharvk','2026-10-03 08:05:59');
/*!40000 ALTER TABLE `active_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_histroy`
--

DROP TABLE IF EXISTS `chat_histroy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_histroy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `user_message` text,
  `bot_response` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_histroy`
--

LOCK TABLES `chat_histroy` WRITE;
/*!40000 ALTER TABLE `chat_histroy` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat_histroy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `competitions`
--

DROP TABLE IF EXISTS `competitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `competitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `description` text,
  `competition_date` date DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `competitions`
--

LOCK TABLES `competitions` WRITE;
/*!40000 ALTER TABLE `competitions` DISABLE KEYS */;
/*!40000 ALTER TABLE `competitions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_categories`
--

DROP TABLE IF EXISTS `event_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `category_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `event_categories_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_categories`
--

LOCK TABLES `event_categories` WRITE;
/*!40000 ALTER TABLE `event_categories` DISABLE KEYS */;
INSERT INTO `event_categories` VALUES (7,5,'Cricket'),(8,5,'Football'),(9,5,'Athletics'),(10,6,'Portrait Photography'),(11,6,'Landscape Photography'),(12,2,'Painting'),(13,2,'Poster Making'),(14,2,'Rangoli'),(15,2,'Sketching'),(16,2,'Digital Art'),(17,1,'Robitics analysis'),(21,3,'Dance'),(22,3,'Natyarang'),(23,3,'Theme walk'),(24,4,'General Registration'),(27,20,'General Registration'),(29,22,'General Registration'),(30,19,'General Registration');
/*!40000 ALTER TABLE `event_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_feedback`
--

DROP TABLE IF EXISTS `event_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `message` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `event_feedback_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_feedback`
--

LOCK TABLES `event_feedback` WRITE;
/*!40000 ALTER TABLE `event_feedback` DISABLE KEYS */;
INSERT INTO `event_feedback` VALUES (6,5,'atharv','1. Overall Rating: 5/5\n2. Organization: 5/5\n3. Content Quality: 4/5\n4. Venue: 4/5\n5. Recommend: Yes\n6. Liked Most: .\n7. Enhancements: .\n8. Suggestions: .','2026-04-30 05:34:13');
/*!40000 ALTER TABLE `event_feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `description` text,
  `category` varchar(50) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `event_time` varchar(20) DEFAULT NULL,
  `price` int DEFAULT '0',
  `image` varchar(200) DEFAULT NULL,
  `organizer` varchar(100) DEFAULT NULL,
  `registration_link` varchar(200) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `venue` varchar(150) DEFAULT NULL,
  `department` varchar(100) DEFAULT 'General',
  `tech_fest_id` int DEFAULT NULL,
  `event_type` varchar(50) DEFAULT 'Individual',
  `reminder_1h_sent` tinyint(1) DEFAULT '0',
  `registration_deadline` datetime DEFAULT NULL COMMENT 'Admin-set deadline after which registrations are closed. NULL means no explicit deadline (uses event_date).',
  `deadline_notif_sent` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_tech_fest` (`tech_fest_id`),
  CONSTRAINT `fk_tech_fest` FOREIGN KEY (`tech_fest_id`) REFERENCES `tech_fests` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'STABILIA Robotics Workshop 2K26','Hands-on robotics workshop','Technical events','2026-05-02','11:15',0,'robo.jpeg','Robotics Club',NULL,'2026-03-12 13:02:20','Main Auditorium','CSE(AIML)',NULL,'Individual',0,'2026-05-01 10:48:00',1),(2,'Kalakruti 2K26','Creative art competitions','Technical events','2026-04-08','12:00',100,'kalakruti.jpeg','Fine Arts Club',NULL,'2026-03-12 13:02:20','Art Gallery','IT',NULL,'Individual',0,NULL,0),(3,'UTOPIA 2K26','Grand cultural festival','Technical events','2026-03-31','16:30',0,'1st.jpeg','Cultural Committee',NULL,'2026-03-12 13:02:20','Open Air Theatre','All Departments',NULL,'Individual',0,NULL,0),(4,'TechVerse Hackathon','48 hour coding challenge','Technical events','2026-03-18','12:15',0,'2nd.jpeg','Tech Club',NULL,'2026-03-12 13:02:20','Computer Lab','IT',NULL,'Group',0,NULL,0),(5,'Sports Day 2K26','Annual sports competition','Technical events','2026-05-30','12:00',0,'sportsday.jpeg','Sports Committee',NULL,'2026-03-12 13:02:20','Sports Ground','IT',NULL,'Individual',0,'2026-05-28 10:00:00',1),(6,'Photography Workshop','Learn professional photography','workshop','2026-03-25','2:00 PM',150,'photography.jpeg','Photography Club',NULL,'2026-03-12 13:02:20','Media Room','IT',NULL,'Individual',0,NULL,0),(19,'Escape the query','SQL QUERIES','Technical events','2026-04-30','10:00',0,'20231117041446_IMG_7404.JPG',NULL,NULL,'2026-04-01 14:33:38','EN1-3','CSE(AIML)',2,'Individual',1,'2026-04-30 10:01:00',1),(20,'Battle code','DSA competition','Tech expo','2026-04-07','10:00',0,'20231116223506_IMG_7233.JPG',NULL,NULL,'2026-04-02 16:35:44','CSE(DEPARMENT)','CSE(AIML)',2,'Individual',0,NULL,0),(22,'CODE HUNT','Event is good.','Technical events','2026-04-21','17:08',0,'trashed-1750945287-IMG_20250209_111555.jpg',NULL,NULL,'2026-04-08 05:03:16','Finolex college','CSE(Cyber Security)',NULL,'Group',0,NULL,0);
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `message` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,'Shrikant','THis website is good','2026-03-29 09:18:10');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `message` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,'New Event Registration ⭐','The stadium is about to explode because Atharv Kudtarkar has officially entered the battle for Sports Day 2K26 Football to bring home the gold! ⚽🔥🏆','2026-04-29 16:32:30','atharv kudtarkar'),(2,'Event Rescheduled','Heads up! \'Escape the query\' has been updated to 2026-04-30 at 10:00.','2026-04-29 16:34:09',NULL),(3,'Registration Deadline Set','Registration for \'Escape the query\' closes on 2026-04-30 10:01. Register before it\'s too late!','2026-04-29 16:34:09',NULL),(4,'New Event Registration ⭐','The pitch is about to ignite because atharv kudtarkar has officially geared up to dominate the Football arena at Sports Day 2K26! ⚽🔥🏆','2026-04-30 00:09:34','atharv kudtarkar'),(5,'New Event Registration ⭐','The countdown begins as atharv kudtarkar officially charges into the arena to dominate the Football field for Sports Day 2K26! ⚽🔥🏟️','2026-04-30 00:23:12','atharv kudtarkar'),(6,'New Event Registration ⭐','Brace yourselves for pure dominance on the turf because atharv kudtarkar is officially locked in for Football at Sports Day 2K26! ⚽️🔥🏟️','2026-04-30 00:44:10','atharv kudtarkar'),(7,'✅ Attendance Marked','Thanks for attending Sports Day 2K26! Your entry was successfully verified.','2026-04-30 00:48:30','atharv kudtarkar'),(8,'New Event Registration ⭐','Huge shoutout to atharv kudtarkar for officially locking in their spot for Escape the query through General Registration! 🚀🔥⚡️','2026-04-30 01:01:13','atharv'),(9,'New Event Registration ⭐','Huge energy today as atharv kudtarkar officially joins the ranks for Escape the query through General Registration, let the games begin! 🚀🔥💻✨','2026-04-30 01:08:34','atharv'),(10,'✅ Attendance Marked','Thanks for attending Escape the query! Your entry was successfully verified.','2026-04-30 01:19:55','atharv'),(11,'New Event Registration ⭐','The pitch is about to ignite as atharv kudtarkar officially gears up for Cricket in the ultimate showdown at Sports Day 2K26! 🏏🔥🏆','2026-04-30 01:20:52','atharv'),(12,'✅ Attendance Marked','Thanks for attending Sports Day 2K26! Your entry was successfully verified.','2026-04-30 01:21:14','atharv'),(13,'New Event Registration ⭐','The stadium is ready to roar because ayush bhuwad has officially entered the arena to dominate Football at Sports Day 2K26! ⚽🔥🏆','2026-04-30 04:18:14','ayush'),(14,'✅ Attendance Marked','Thanks for attending Sports Day 2K26! Your entry was successfully verified.','2026-04-30 04:19:51','ayush'),(15,'Event Rescheduled','Heads up! \'STABILIA Robotics Workshop 2K26\' has been updated to 2026-04-20 at 11:15.','2026-04-30 04:21:10',NULL),(16,'Registration Cancelled ❌','Your registration for \'Sports Day 2K26\' has been cancelled by the administrator. Reason: due to so  many entries','2026-04-30 04:26:37','ayush bhuwad'),(17,'Registration Closed','Registration for \'Escape the query\' is now CLOSED (deadline: 30 Apr 2026 at 10:01 AM). Contact the admin if you still want to participate.','2026-04-30 04:33:08',NULL),(18,'You\'re In! Registration Closed','Registration for \'Escape the query\' is now closed. You\'re already in — just show up on the event day!','2026-04-30 04:33:08','atharv kudtarkar'),(19,'New Event Registration ⭐','The pitch is about to ignite because Ayush Bhuwad has officially registered for Cricket at Sports Day 2K26 and is ready to knock it out of the park! 🏏🔥⚡🏟️','2026-04-30 04:56:52','ayush'),(20,'New Event Registration ⭐','Massive shoutout to ayush bhuwad for officially locking in their spot for Cricket at Sports Day 2K26 and getting ready to smash it out of the park! 🏏🔥⚡️🏆','2026-04-30 05:09:48','ayush'),(21,'New Event Registration ⭐','Get ready for some absolute fireworks on the pitch because ayush bhuwad has officially registered to dominate the Cricket module at Sports Day 2K26! 🏏🔥🏆','2026-04-30 05:09:50','ayush'),(22,'New Event Registration ⭐','The track is about to catch fire because atharv kudtarkar just officially registered to dominate Athletics at Sports Day 2K26! 🏃‍♂️🔥🏆','2026-04-30 05:24:48','atharv'),(23,'✅ Attendance Marked','Thanks for attending Sports Day 2K26! Your entry was successfully verified.','2026-04-30 05:26:10','atharv'),(24,'Registration Cancelled ❌','Your registration for \'Sports Day 2K26\' has been cancelled by the administrator. Reason: due to specicic reason','2026-04-30 05:26:58','atharv kudtarkar'),(25,'Event Rescheduled','Heads up! \'STABILIA Robotics Workshop 2K26\' has been updated to 2026-05-02 at 11:15.','2026-04-30 05:28:39',NULL),(26,'Registration Deadline Set','Registration for \'STABILIA Robotics Workshop 2K26\' closes on 2026-05-01 10:48. Register before it\'s too late!','2026-04-30 05:28:39',NULL),(27,'Registration Closed','Registration for \'STABILIA Robotics Workshop 2K26\' is now CLOSED (deadline: 01 May 2026 at 10:48 AM). Contact the admin if you still want to participate.','2026-05-02 06:11:08',NULL),(28,'Registration Cancelled ❌','Your registration for \'Sports Day 2K26\' has been cancelled by the administrator. Reason: .','2026-05-26 05:19:33','atharv kudtarkar'),(29,'Registration Cancelled ❌','Your registration for \'Escape the query\' has been cancelled by the administrator. Reason: .','2026-05-26 05:19:47','atharv kudtarkar'),(30,'Registration Cancelled ❌','Your registration for \'Sports Day 2K26\' has been cancelled by the administrator. Reason: .','2026-05-26 05:20:00','atharv kudtarkar'),(31,'Event Rescheduled','Heads up! \'Sports Day 2K26\' has been updated to 2026-05-30 at 12:00.','2026-05-26 05:23:31',NULL),(32,'Registration Deadline Set','Registration for \'Sports Day 2K26\' closes on 2026-05-28 10:00. Register before it\'s too late!','2026-05-26 05:23:31',NULL),(33,'New Event Registration ⭐','The roar of the stadium awaits as Atharv Kudtarkar officially registers to crush it on the pitch for the legendary Sports Day 2K26 Cricket tournament! 🏏🔥⚡🏆','2026-05-26 05:26:31','Atharvk'),(34,'✅ Attendance Marked','Thanks for attending Sports Day 2K26! Your entry was successfully verified.','2026-05-26 05:31:59','Atharvk');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration`
--

DROP TABLE IF EXISTS `registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `registration_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `registration_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `event_categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration`
--

LOCK TABLES `registration` WRITE;
/*!40000 ALTER TABLE `registration` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registrations`
--

DROP TABLE IF EXISTS `registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `event_id` int DEFAULT NULL,
  `registered_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registrations`
--

LOCK TABLES `registrations` WRITE;
/*!40000 ALTER TABLE `registrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `registrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registrations_new`
--

DROP TABLE IF EXISTS `registrations_new`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registrations_new` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `branch` varchar(50) DEFAULT NULL,
  `class` varchar(50) DEFAULT NULL,
  `team_name` varchar(255) DEFAULT NULL,
  `ticket_id` varchar(100) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Registered',
  `payment_status` varchar(20) DEFAULT 'Pending',
  `transaction_id` varchar(100) DEFAULT NULL,
  `account_username` varchar(50) DEFAULT NULL,
  `attendance_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registrations_new`
--

LOCK TABLES `registrations_new` WRITE;
/*!40000 ALTER TABLE `registrations_new` DISABLE KEYS */;
INSERT INTO `registrations_new` VALUES (11,5,7,'ayush bhuwad','ayushbhuwad0811@gmail.com','9371528166','CSE','SY',NULL,'98673619C77B','Registered','Completed',NULL,'ayush',NULL);
/*!40000 ALTER TABLE `registrations_new` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tech_fests`
--

DROP TABLE IF EXISTS `tech_fests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tech_fests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `department` varchar(100) NOT NULL,
  `description` text,
  `fest_date` date DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `show_on_home` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tech_fests`
--

LOCK TABLES `tech_fests` WRITE;
/*!40000 ALTER TABLE `tech_fests` DISABLE KEYS */;
INSERT INTO `tech_fests` VALUES (2,'Quantextera','CSE(AIML)','IT is fully competitive event which analysed your coding skills   and als0 problem solving skills','2026-04-16','CSE(DEPARMENT)','trashed-1750945287-IMG_20250209_111555.jpg','2026-04-01 14:32:33',1);
/*!40000 ALTER TABLE `tech_fests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_activity_log`
--

DROP TABLE IF EXISTS `user_activity_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_activity_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `action_type` varchar(100) NOT NULL,
  `action_details` text,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activity_log`
--

LOCK TABLES `user_activity_log` WRITE;
/*!40000 ALTER TABLE `user_activity_log` DISABLE KEYS */;
INSERT INTO `user_activity_log` VALUES (1,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Football\'. Ticket: C18854230EB6','2026-04-29 22:02:30'),(2,'atharv','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-04-29 22:02:41'),(3,'atharv','LOGIN','User logged into the system.','2026-04-29 22:04:35'),(4,'atharv','LOGIN','User logged into the system.','2026-04-30 05:39:05'),(5,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Football\'. Ticket: E0A501CABAB0','2026-04-30 05:39:34'),(6,'atharv','LOGIN','User logged into the system.','2026-04-30 05:52:38'),(7,'atharv','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-04-30 05:52:45'),(8,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Football\'. Ticket: 236688E38E70','2026-04-30 05:53:12'),(9,'atharv','LOGIN','User logged into the system.','2026-04-30 06:13:31'),(10,'atharv','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-04-30 06:13:41'),(11,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Football\'. Ticket: DF2F6F95BDDC','2026-04-30 06:14:10'),(12,'atharv','LOGIN','User logged into the system.','2026-04-30 06:17:58'),(13,'atharv','LOGIN','User logged into the system.','2026-04-30 06:19:41'),(14,'atharv','LOGIN','User logged into the system.','2026-04-30 06:19:47'),(15,'atharv','LOGIN','User logged into the system.','2026-04-30 06:30:54'),(16,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Escape the query\' in category \'General Registration\'. Ticket: 65A1B44EAA79','2026-04-30 06:31:13'),(17,'atharv','CANCEL_REGISTRATION','Cancelled registration for event \'Escape the query\'.','2026-04-30 06:37:49'),(18,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Escape the query\' in category \'General Registration\'. Ticket: FCCEAF31B19D','2026-04-30 06:38:34'),(19,'atharv','LOGIN','User logged into the system.','2026-04-30 06:47:00'),(20,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Cricket\'. Ticket: 0C86A589EB8D','2026-04-30 06:50:52'),(21,'atharv','LOGIN','User logged into the system.','2026-04-30 09:16:29'),(22,'atharv','ASK_AI','Asked: tell me about events','2026-04-30 09:18:25'),(23,'atharv','ASK_AI','Asked: tell me about event','2026-04-30 09:18:53'),(24,'atharv','LOGIN','User logged into the system.','2026-04-30 09:31:12'),(25,'atharv','LOGIN','User logged into the system.','2026-04-30 09:36:00'),(26,'atharv','ASK_AI','Asked: what are upcoming events','2026-04-30 09:37:18'),(27,'atharv','LOGIN','User logged into the system.','2026-04-30 09:41:46'),(28,'ayush','LOGIN','User logged into the system.','2026-04-30 09:46:52'),(29,'ayush bhuwad','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Football\'. Ticket: F31ACEE384F1','2026-04-30 09:48:14'),(30,'ayush','LOGIN','User logged into the system.','2026-04-30 09:52:04'),(31,'ayush','ASK_AI','Asked: what are upcoming events','2026-04-30 09:53:18'),(32,'ayush','ASK_AI','Asked: can i do  rregistrtion for techverse hackthon','2026-04-30 09:53:55'),(33,'ayush','LOGIN','User logged into the system.','2026-04-30 10:09:02'),(34,'ayush bhuwad','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Cricket\'. Ticket: CCF673DE5116','2026-04-30 10:26:52'),(35,'ayush','LOGIN','User logged into the system.','2026-04-30 10:33:29'),(36,'ayush','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-04-30 10:39:22'),(37,'ayush bhuwad','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Cricket\'. Ticket: D8327755237F','2026-04-30 10:39:48'),(38,'ayush bhuwad','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Cricket\'. Ticket: 98673619C77B','2026-04-30 10:39:50'),(39,'ayush','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-04-30 10:40:13'),(40,'ayush','LOGIN','User logged into the system.','2026-04-30 10:46:16'),(41,'atharv','LOGIN','User logged into the system.','2026-04-30 10:53:53'),(42,'atharv kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Athletics\'. Ticket: 7E1FCD320A0B','2026-04-30 10:54:48'),(43,'atharv','LOGIN','User logged into the system.','2026-04-30 10:59:06'),(44,'atharv','ASK_AI','Asked: tell me about upcoming events','2026-04-30 11:00:59'),(45,'atharv','ASK_AI','Asked: tell about evnts','2026-04-30 11:01:18'),(46,'atharv','ASK_AI','Asked: tell me about upcoming event','2026-04-30 11:01:43'),(47,'atharv','ASK_AI','Asked: what are past events that are cocncluded','2026-04-30 11:02:15'),(48,'atharv','ASK_AI','Asked: what are past events in april month','2026-04-30 11:02:44'),(49,'atharv','ASK_AI','Asked: what a re  past events in april','2026-04-30 11:03:14'),(50,'atharv','FEEDBACK_SUBMISSION','Submitted feedback for event \'Sports Day 2K26\'. Overall Rating: 5/5','2026-04-30 11:04:13'),(51,'atharv','LOGIN','User logged into the system.','2026-04-30 11:04:55'),(52,'atharv','LOGIN','User logged into the system.','2026-05-02 11:41:29'),(53,'atharv','LOGIN','User logged into the system.','2026-05-26 10:46:10'),(54,'atharv','ASK_AI','Asked: hello','2026-05-26 10:46:18'),(55,'atharv','ASK_AI','Asked: what are upcoming events should be concluded','2026-05-26 10:47:26'),(56,'atharv','ASK_AI','Asked: What events should come for next seson','2026-05-26 10:48:07'),(57,'atharv','LOGIN','User logged into the system.','2026-05-26 10:50:20'),(58,'Atharvk','LOGIN','User logged into the system.','2026-05-26 10:52:20'),(59,'Atharvk','LOGIN','User logged into the system.','2026-05-26 10:54:15'),(60,'Atharv Kudtarkar','EVENT_REGISTRATION','Registered for \'Sports Day 2K26\' in category \'Cricket\'. Ticket: EE4E446870B8','2026-05-26 10:56:31'),(61,'Atharvk','LOGIN','User logged into the system.','2026-05-26 11:02:49'),(62,'Atharvk','LOGIN','User logged into the system.','2026-05-26 11:03:22'),(63,'Atharvk','CANCEL_REGISTRATION','Cancelled registration for event \'Sports Day 2K26\'.','2026-05-26 11:05:44'),(64,'Atharvk','ASK_AI','Asked: Hello ','2026-05-26 11:07:30'),(65,'testuser','LOGIN','User logged into the system.','2026-06-13 18:14:05'),(66,'Atharvk','LOGIN','User logged into the system.','2026-10-03 13:08:52'),(67,'Atharvk','ASK_AI','Asked: tell me about latest events','2026-10-03 13:09:47'),(68,'Atharvk','LOGIN','User logged into the system.','2026-10-03 13:12:14'),(69,'Atharvk','ASK_AI','Asked: what are latest events are there','2026-10-03 13:22:05'),(70,'Atharvk','ASK_AI','Asked: waht are upcoming events are there','2026-10-03 13:22:42'),(71,'Atharvk','ASK_AI','Asked: i means upcoming but this re hled events earlier','2026-10-03 13:23:03'),(72,'Atharvk','LOGIN','User logged into the system.','2026-10-03 13:31:08'),(73,'Atharvk','ASK_AI','Asked: what are events currently','2026-10-03 13:31:20'),(74,'Atharvk','ASK_AI','Asked: but wich are upcomig','2026-10-03 13:31:35'),(75,'Atharvk','ASK_AI','Asked: no i mean which are upcoming events','2026-10-03 13:31:50'),(76,'Atharvk','LOGIN','User logged into the system.','2026-10-03 13:35:59'),(77,'Atharvk','ASK_AI','Asked: what are latest events','2026-10-03 13:36:07');
/*!40000 ALTER TABLE `user_activity_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `class` varchar(50) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (29,'parth','scrypt:32768:8:1$jgEMoSlQH9Ost6Kh$eb79e33f8c4e06b8d9ab564aca7885c202ffcd454e1b6c13794f94bcd257b3e4e9b20be75270404577f2577c4803d35a690b2f1335ab826e27ce7af046bde01c','atharvkudtarkar4406@gmail.com','Se-css','7588271179'),(30,'atharv','scrypt:32768:8:1$2z9Fumxzra4shZOh$b513c3379292d19a5c580838dea3f12573ddfaa682313bbba0b4616e88f87539f04951f1a51774c0500ba0db4c205440a1340cd203146918c706441b248c4faa','atharvk4406@gmail.com','Se-css','7588271179'),(31,'ayush','scrypt:32768:8:1$I7U2WNxmGjpjvJiE$e2e14aed27631776e0e066a7a73695985e740be27e635ff138da3d54ee8a2d7aca36c93db256830bf242059715b4d73c337e0a04066edf335c5a53d88ce22aff','ayushbhuwad0811@gmail.com','SE-CSE','9371528166'),(32,'sagar','scrypt:32768:8:1$aP5L0lE9a8BL1Nk2$dff022e38b1e94a38c6c8c22e37386a8321b31d7d478dec831fa28c5b4eecaaef3c102f5880001e555fe0f5924f59f5c7864b872c37a6d67c950aeb997588de7','sagar.harne@gmail.com','SE-CSE','7899086767'),(33,'Atharvk','scrypt:32768:8:1$lyCsQhkMC4u9zMru$673d3104e8e717b9c41911af71989fd06cd0d7dde3203f19d7c561a646db1e85637f11b47b005819ef78e006cd2134652f1b6be1537cdf29a882ca29ad5ade8b','apkudtarkar4406@gmail.cm','SE-CSE','7588271179'),(34,'testuser','scrypt:32768:8:1$9g9VMM0UmyKK7I4J$eaca00c3771bd69bf182c6eb368391c1310896a9ebe2504af6c308c34b878093ca3cc91a4e5242dc359b0f6a6cfe07786c128b2c5dbe0a94a245a3de2e13da06','testuser@example.com','TE-IT','9876543210');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-03 19:50:25
