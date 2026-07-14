CREATE TABLE events (
ID int,
event varchar(255),
YEAR INt,
GOLD varchar(255),
SILVER varchar(255),
BRONZE varchar(255)
);

delete from events;

INSERT INTO events VALUES (1,'100m',2016, 'Amthhew Mcgarray','donald','barbara');
INSERT INTO events VALUES (2,'200m',2016, 'Nichole','Alvaro Eaton','janet Smith');
INSERT INTO events VALUES (3,'500m',2016, 'Charles','Nichole','Susana');
INSERT INTO events VALUES (4,'100m',2016, 'Ronald','maria','paula');
INSERT INTO events VALUES (5,'200m',2016, 'Alfred','carol','Steven');
INSERT INTO events VALUES (6,'500m',2016, 'Nichole','Alfred','Brandon');
INSERT INTO events VALUES (7,'100m',2016, 'Charles','Dennis','Susana');
INSERT INTO events VALUES (8,'200m',2016, 'Thomas','Dawn','catherine');
INSERT INTO events VALUES (9,'500m',2016, 'Thomas','Dennis','paula');
INSERT INTO events VALUES (10,'100m',2016, 'Charles','Dennis','Susana');
INSERT INTO events VALUES (11,'200m',2016, 'jessica','Donald','Stefeney');
INSERT INTO events VALUES (12,'500m',2016,'Thomas','Steven','Catherine');

select * from events; 


-- write a query to find no of gold medals per swimmer who won only gold medals 

-- Approach 1 

SELECT 
  gold,
  count(1) as countGold
FROM 
  events 
WHERE 
  gold NOT IN (SELECT silver FROM events WHERE silver IS NOT NULL) 
  AND 
  gold NOT IN (SELECT bronze FROM events WHERE bronze IS NOT NULL)
group by 
  gold ;


-- Approach 2 

-- ============================================================
-- Same idea as Approach 2, but more compact: a swimmer qualifies if their
-- rows collapse to exactly ONE distinct medal_type, and that type is gold.
 
with cte as (
 select gold as player_name,'gold' as medal_type from events
 union all select silver,'silver' as medal_type from events
 union all select bronze,'bronze' as medal_type from events
)
select
  player_name,
  count(1) as no_of_gold_medals
from
  cte
group by
  player_name
having
  count(distinct medal_type) = 1
  and max(medal_type) = 'gold';
 
 
-- ============================================================
-- Approach 3: single NOT IN with UNION ALL of silver + bronze
-- ============================================================
-- Same logic as Approach 1, but silver and bronze are combined into
-- one subquery via UNION ALL instead of two separate NOT IN clauses.
 
select
  gold as player_name,
  count(1) as no_of_medals
from
  events
where
  gold not in (select silver from events union all select bronze from events)
group by
  gold;





