CREATE TYPE "Status" AS ENUM (
  'ACTIVE',
  'INACTIVE'
);

CREATE TYPE "Month" AS ENUM (
  'JAN',
  'FEB',
  'MAR',
  'APR',
  'MAY',
  'JUN',
  'JUL',
  'AUG',
  'SEP',
  'OCT',
  'NOV',
  'DEC'
);

CREATE TABLE "Users" (
  "id" uuid PRIMARY KEY,
  "username" varchar,
  "role" varchar,
  "status" "Status",
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "Account" (
  "id" uuid PRIMARY KEY,
  "owner" uuid NOT NULL,
  "name" string,
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "AccountMonthSnapshot" (
  "id" uuid PRIMARY KEY,
  "month" "Month",
  "year" date,
  "account" uuid,
  "ingress" uuid,
  "egress" uuid,
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "AccountSummaryIngressDetails" (
  "id" uuid PRIMARY KEY,
  "total" string DEFAULT 0,
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "AccountSummaryIngressEvent" (
  "id" uuid PRIMARY KEY,
  "total" string DEFAULT 0,
  "date_posted" datetime,
  "source" "IngressSource",
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "IngresSource" (
  "id" uuid PRIMARY KEY,
  "name" string,
  "created_at" datetime,
  "modified_at" datetime
);

CREATE TABLE "EgressSource" (
  "id" uuid PRIMARY KEY,
  "name" string,
  "created_at" datetime,
  "modified_at" datetime
);

CREATE TABLE "AccountSummaryEgressDetailsSourceEvent" (
  "id" uuid PRIMARY KEY,
  "event" uuid,
  "details" uuid,
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "AccountSummaryEgressEvent" (
  "id" uuid PRIMARY KEY,
  "total" string DEFAULT 0,
  "date_posted" datetime,
  "source" "EgressSource",
  "created_at" timestamp,
  "modified_at" timestamp
);

CREATE TABLE "AccountSummaryInressDetailsSourceEvent" (
  "id" uuid PRIMARY KEY,
  "details" uuid,
  "event" uuid,
  "created_at" datetime,
  "modified_at" datetime
);

CREATE TABLE "AccountSummaryEgressDetails" (
  "id" uuid PRIMARY KEY,
  "total" string DEFAULT 0,
  "created_at" timestamp,
  "modified_at" timestamp
);

COMMENT ON COLUMN "Account"."name" IS 'Account conanical name';

COMMENT ON COLUMN "IngresSource"."name" IS 'User-Defined Source';

COMMENT ON COLUMN "EgressSource"."name" IS 'User-Defined Source';

ALTER TABLE "AccountMonthSnapshot" ADD FOREIGN KEY ("account") REFERENCES "Account" ("id");

ALTER TABLE "AccountMonthSnapshot" ADD FOREIGN KEY ("ingress") REFERENCES "AccountSummaryIngressDetails" ("id");

ALTER TABLE "AccountMonthSnapshot" ADD FOREIGN KEY ("egress") REFERENCES "AccountSummaryEgressDetails" ("id");

ALTER TABLE "AccountSummaryIngressEvent" ADD FOREIGN KEY ("source") REFERENCES "IngresSource" ("id");

ALTER TABLE "AccountSummaryEgressDetailsSourceEvent" ADD FOREIGN KEY ("event") REFERENCES "AccountSummaryEgressEvent" ("id");

ALTER TABLE "AccountSummaryEgressDetailsSourceEvent" ADD FOREIGN KEY ("details") REFERENCES "AccountSummaryEgressDetails" ("id");

ALTER TABLE "AccountSummaryEgressEvent" ADD FOREIGN KEY ("source") REFERENCES "EgressSource" ("id");

ALTER TABLE "AccountSummaryInressDetailsSourceEvent" ADD FOREIGN KEY ("details") REFERENCES "AccountSummaryIngressDetails" ("id");

ALTER TABLE "AccountSummaryIngressEvent" ADD FOREIGN KEY ("id") REFERENCES "AccountSummaryInressDetailsSourceEvent" ("event");
