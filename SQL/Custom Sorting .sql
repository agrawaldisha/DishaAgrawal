
-- 🧾 Problem Statement

-- You are given a table team_details containing names of different teams.

-- Write an SQL query to:

-- Display all team names
-- Ensure that "India" always appears at the top of the result
-- Sort the remaining teams in alphabetical order

create table team_details(
  team varchar(20)
);

insert into team_details values ("India");
insert into team_details values ("Australia");
insert into team_details values ("Canada");
insert into team_details values ("Beijing");

select team from team_details order by team;

select team from team_details 
order by 
case 
when team = 'India' then 0 
else 1 
end,
team;