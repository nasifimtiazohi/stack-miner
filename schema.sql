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


CREATE TABLE `crashpatch`.`cpes` (
  `cveID` INT NOT NULL,
  `cpe` VARCHAR(45) NULL,
  `part` VARCHAR(45) NULL,
  `vendor` VARCHAR(255) NULL,
  `product` VARCHAR(255) NULL,
  `version` VARCHAR(255) NULL,
  `update` VARCHAR(255) NULL,
  `edition` VARCHAR(255) NULL,
  `language` VARCHAR(255) NULL,
  `rest` VARCHAR(255) NULL);

  CREATE TABLE cvss (
    cve character(20) NOT NULL,
    attack_complexity_3 character(5),
    attack_vector_3 character(20),
    availability_impact_3 character(5),
    confidentiality_impact_3 character(5),
    integrity_impact_3 character(5),
    privileges_required_3 character(5),
    scope_3 character(10),
    user_interaction_3 character(10),
    vector_string_3 character(50),
    exploitability_score_3 real,
    impact_score_3 real,
    base_score_3 real,
    base_severity_3 character(10),
    access_complexity character(10),
    access_vector character(20),
    authentication character(10),
    availability_impact character(10),
    confidentiality_impact character(10),
    integrity_impact character(10),
    obtain_all_privileges boolean,
    obtain_other_privileges boolean,
    obtain_user_privileges boolean,
    user_interaction_required boolean,
    vector_string character(50),
    exploitability_score real,
    impact_score real,
    base_score real,
    severity character(10),
    description text,
    published_date date,
    last_modified_date date
);

CREATE TABLE affected_products (
    cve character(20) NOT NULL,
    vendor_name text,
    product_name text,
    version_value text
);

CREATE TABLE cpe (
    cve character(20) NOT NULL,
    cpe22uri text,
    cpe23uri text,
    vulnerable character(5)
);

CREATE TABLE cve_problem (
    cve character(20) NOT NULL,
    problem text
);

-- use this to convert tables whenever an illegal mix of collation happens
ALTER TABLE relatedPackages CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;