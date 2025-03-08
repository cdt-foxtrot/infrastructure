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
  health decimal(3, 1),
  CONSTRAINT service_pk PRIMARY KEY (service)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Inits Starting Data for Table
INSERT INTO scoring (box, service, health) values (1, "AD/DNS", 20);
INSERT INTO scoring (box, service, health) values (2, "Apache", 20);
INSERT INTO scoring (box, service, health) values (3, "ELK", 20);
INSERT INTO scoring (box, service, health) values (4, "IIS/FTP", 20);
INSERT INTO scoring (box, service, health) values (5, "Mail", 20);
INSERT INTO scoring (box, service, health) values (6, "MySQL", 20);
INSERT INTO scoring (box, service, health) values (7, "Nginx", 20);
INSERT INTO scoring (box, service, health) values (8, "NTP", 20);
INSERT INTO scoring (box, service, health) values (9, "Samba", 20);
INSERT INTO scoring (box, service, health) values (10, "WinRM", 20);