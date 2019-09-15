-- DROP SCHEMA IF EXISTS `crashpatch`;
-- this schema is outdated. update schema after database designing is complete.

CREATE SCHEMA `crashpatch` ;

CREATE TABLE `crashpatch`.`crashes` (
  `crashID` INT NOT NULL,
  `component` VARCHAR(255) NULL,
  `crashFunction` LONGTEXT NULL,
  `status` VARCHAR(45) NULL,
  `type` VARCHAR(255) NULL,
  `lastDate` DATETIME NULL,
  `firstDate` DATETIME NULL,
  `count` INT NULL,
  PRIMARY KEY (`Crash_ID`));

CREATE TABLE `crashpatch`.`backtrace` (
  `crashID` INT NOT NULL,
  `function` LONGTEXT NULL,
  `binary` LONGTEXT NULL,
  `source` LONGTEXT NULL,
  `line` INT NULL,
  PRIMARY KEY (`crashID`));

CREATE TABLE `crashpatch`.`relatedPackages` (
  `crashID` INT NOT NULL,
  `package` VARCHAR(45) NULL,
  `version` LONGTEXT NULL,
  `count` INT NULL,
  PRIMARY KEY (`crashID`));


CREATE TABLE `crashpatch`.`crashReport` (
  `crashID` INT NOT NULL,
  `problemID` INT NULL,
  `executable` LONGTEXT NULL,
  `errorName` VARCHAR(255) NULL,
  `created` DATETIME NULL,
  `lastChange` DATETIME NULL,
  `uniqueReports` INT NULL,
  `externalBug` LONGTEXT NULL,
  PRIMARY KEY (`crashID`));

  CREATE TABLE `crashpatch`.`os` (
  `crashID` INT NOT NULL,
  `os` VARCHAR(255) NULL,
  `uniqueCount` INT NULL,
  `totalCount` INT NULL,
  PRIMARY KEY (`crashID`));

  CREATE TABLE `crashpatch`.`architecture` (
  `crashID` INT NOT NULL,
  `architecture` VARCHAR(255) NULL,
  `count` INT NULL,
  PRIMARY KEY (`crashID`));


-- https://retrace.fedoraproject.org/faf/reports/?opsysreleases=127&component_names=&associate=__None&daterange=2018-09-01%3A2019-09-01&order_by=last_occurrence