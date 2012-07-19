/* This program is free software. It comes without any warranty, to
* the extent permitted by applicable law. You can redistribute it
* and/or modify it under the terms of the Do What The Fuck You Want
* To Public License, Version 2, as published by Sam Hocevar. See
* http://sam.zoy.org/wtfpl/COPYING for more details. */

PRAGMA foreign_keys = false;

CREATE TABLE IF NOT EXISTS "community_choice" (
	 "id" integer NOT NULL,
	 "kind" text NOT NULL,
	 "name" text NOT NULL,
	 "discount" integer NOT NULL,
	 "before_price" text NOT NULL,
	 "now_price" text NOT NULL,
	 "end_date" integer NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "flash_sale" (
	 "id" integer NOT NULL,
	 "kind" text NOT NULL,
	 "name" text NOT NULL,
	 "discount" integer NOT NULL,
	 "before_price" text NOT NULL,
	 "now_price" text NOT NULL,
	 "end_date" integer NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "vote_candidates" (
	 "id" integer NOT NULL,
	 "candidates" text NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "vote_results" (
     "last_timestamp" integer NOT NULL,
     "result" text NOT NULL
);

PRAGMA foreign_keys = true;
