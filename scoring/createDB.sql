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
  service varchar(10),
  health tinyint,
  CONSTRAINT service_pk PRIMARY KEY (service)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Inits Starting Data for Table
INSERT INTO scoring (service, health) values ("AD/DNS", 20);
INSERT INTO scoring (service, health) values ("IIS/FTP", 20);
INSERT INTO scoring (service, health) values ("Nginx", 20);
INSERT INTO scoring (service, health) values ("WinRM", 20);
INSERT INTO scoring (service, health) values ("Apache", 20);
INSERT INTO scoring (service, health) values ("MySQL", 20);
INSERT INTO scoring (service, health) values ("Mail", 20);
INSERT INTO scoring (service, health) values ("Samba", 20);
INSERT INTO scoring (service, health) values ("ELK", 20);
INSERT INTO scoring (service, health) values ("NTP", 20);