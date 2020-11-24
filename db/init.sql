sudo -u postgres psql
create user medbot with password '3285';
create database medbot with owner medbot;