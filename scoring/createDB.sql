-- Creates Greyteam User if not already made (Needed for Py Script)
CREATE USER IF NOT EXISTS 'greyteam'@'localhost' IDENTIFIED BY 'greyteam';
GRANT ALL PRIVILEGES ON *.* TO 'greyteam'@'localhost';
FLUSH PRIVILEGES;  

-- Inits New Comp DB
DROP DATABASE IF EXISTS Scoring;
CREATE DATABASE Scoring;
USE Scoring;

-- Inits New Scoring Table
DROP TABLE IF EXISTS scoring;
CREATE TABLE scoring (
  box tinyint,
  service varchar(10),
  building varchar(10),
  os varchar(30),
  ip varchar (15),
  port varchar (20),
  health decimal(3, 1) unsigned,
  state varchar(4),
  CONSTRAINT service_pk PRIMARY KEY (service)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Inits Starting Data for Table
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (1, "AD/DNS", "River", "Windows", "10.150.1.1", "139", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (5, "Apache", "Plains", "Ubuntu", "10.150.1.5", "80", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (10, "ELK", "Desert", "Ubuntu", "10.150.1.10", "9200,5044,5601", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (2, "IIS", "Swamp", "Windows", "10.150.1.2", "80", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (7, "Mail", "Savanna", "Ubuntu", "10.150.1.7", "143,993", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (6, "MySQL", "Forest", "Ubuntu", "10.150.1.6", "3306", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (3, "Nginx", "Beach", "Windows", "10.150.1.3", "80", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (8, "FTP", "Taiga", "Ubuntu", "10.150.1.8", "21", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (9, "Samba", "Jungle", "Ubuntu", "10.150.1.9", "139", 20, "UP");
INSERT INTO scoring (box, service, building, os, ip, port, health, state) values (4, "WinRM", "Ocean", "Windows", "10.150.1.4", "5985", 20, "UP");
