
-- Enable FK constraints
PRAGMA FOREIGN_KEYS = ON;

-- Students table
DROP TABLE IF EXISTS "students";
CREATE TABLE IF NOT EXISTS "students" (
  "sid" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
  "first" VARCHAR NOT NULL,
  "last" VARCHAR NOT NULL);

-- Quizzes table
DROP TABLE IF EXISTS "quizzes";
CREATE TABLE IF NOT EXISTS "quizzes" (
  "qid" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,
  "date" DATETIME NOT NULL ,
  "subj" VARCHAR NOT NULL ,
  "numq" VARCHAR NOT NULL );

-- Results table
DROP TABLE IF EXISTS "results";
CREATE TABLE "results"
(
    "rid" INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL UNIQUE,
    "sid" INTEGER REFERENCES students("sid") ON DELETE SET NULL,
    "qid" INTEGER REFERENCES quizzes("qid") ON DELETE SET NULL,
    "score" FLOAT
);

DROP INDEX IF EXISTS sid_idx;
CREATE INDEX sid_idx on results("sid");
DROP INDEX IF EXISTS qid_idx;
CREATE INDEX qid_idx on results("qid");

-- Initial data
INSERT INTO "students" (first, last) VALUES ('John', 'Smith');
INSERT INTO "quizzes" (date, subj, numq) VALUES ('2015-02-05', 'Python Basics', '5');
INSERT INTO "results" (sid, qid, score) VALUES (1, 1, 85.0);
