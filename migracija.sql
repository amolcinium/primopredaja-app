-- ============================================================
-- PRIMOPREDAJA — praćenje završnih radova i dorada
-- Pokreni cijeli fajl u Supabase: SQL Editor -> New query -> Run
-- ============================================================

-- 1) TABELE -----------------------------------------------------
create table if not exists zgrade (
  id uuid primary key default gen_random_uuid(),
  naziv text not null,
  broj_stanova int default 0,
  created_at timestamptz default now()
);

create table if not exists stanovi (
  id uuid primary key default gen_random_uuid(),
  zgrada_id uuid references zgrade(id) on delete cascade,
  oznaka text not null,
  sprat text,
  kvadratura numeric,
  tip_grijanja text check (tip_grijanja in ('Električno podno','Vodeno podno + kotao')),
  status_primopredaje text default 'Čeka'
     check (status_primopredaje in ('Čeka','Zakazana','Primopredato','Odbijena')),
  redoslijed int default 0,
  created_at timestamptz default now(),
  unique (zgrada_id, oznaka)
);

create table if not exists stavke (
  id int primary key,
  prostorija text not null,
  naziv text not null,
  redoslijed int not null
);

create table if not exists provjere (
  id uuid primary key default gen_random_uuid(),
  stan_id uuid references stanovi(id) on delete cascade,
  stavka_id int references stavke(id),
  status text check (status in ('OK','X','DORADA','N/P')),
  napomena text,
  ime text,
  updated_at timestamptz default now(),
  unique (stan_id, stavka_id)
);

create table if not exists dorade (
  id uuid primary key default gen_random_uuid(),
  stan_id uuid references stanovi(id) on delete cascade,
  stavka_id int references stavke(id),
  prostorija text,
  detalj text,
  opis text,
  izvodjac text,
  prioritet text default 'Normalan' check (prioritet in ('Kritičan','Visok','Normalan')),
  status text default 'Otvoreno'
     check (status in ('Otvoreno','U doradi','Popravljeno - čeka kontrolu','Provjereno OK','Odustalo')),
  rok date,
  foto_prije text,
  foto_poslije text,
  kontrolisao text,
  datum_prijave timestamptz default now(),
  datum_zatvaranja timestamptz
);

create index if not exists idx_provjere_stan on provjere(stan_id);
create index if not exists idx_dorade_stan on dorade(stan_id);
create index if not exists idx_dorade_status on dorade(status);

-- 2) AUTO-DORADA TRIGER ----------------------------------------
-- X  -> automatski otvori doradu (ako već ne postoji otvorena)
-- OK -> automatski zatvori otvorenu doradu za taj stan+stavku
create or replace function fn_auto_dorada() returns trigger as $$
begin
  if NEW.status = 'X' then
    if not exists (select 1 from dorade d
                   where d.stan_id = NEW.stan_id and d.stavka_id = NEW.stavka_id
                     and d.status not in ('Provjereno OK','Odustalo')) then
      insert into dorade (stan_id, stavka_id, prostorija, detalj, opis, status)
      select NEW.stan_id, NEW.stavka_id, s.prostorija, s.naziv, NEW.napomena, 'Otvoreno'
      from stavke s where s.id = NEW.stavka_id;
    end if;
  elsif NEW.status = 'OK' then
    update dorade set status='Provjereno OK', datum_zatvaranja=now()
    where stan_id = NEW.stan_id and stavka_id = NEW.stavka_id
      and status not in ('Provjereno OK','Odustalo');
  end if;
  NEW.updated_at = now();
  return NEW;
end; $$ language plpgsql;

drop trigger if exists trg_auto_dorada on provjere;
create trigger trg_auto_dorada
  before insert or update on provjere
  for each row execute function fn_auto_dorada();

-- 3) RLS (shared-code model: samo prijavljeni imaju pristup) ----
alter table zgrade   enable row level security;
alter table stanovi  enable row level security;
alter table stavke   enable row level security;
alter table provjere enable row level security;
alter table dorade   enable row level security;

do $$
declare t text;
begin
  foreach t in array array['zgrade','stanovi','stavke','provjere','dorade'] loop
    execute format('drop policy if exists auth_all on %I', t);
    execute format('create policy auth_all on %I for all to authenticated using (true) with check (true)', t);
  end loop;
end $$;

-- 4) STORAGE bucket za fotografije ------------------------------
insert into storage.buckets (id, name, public)
values ('fotografije','fotografije', true)
on conflict (id) do nothing;

drop policy if exists foto_upload on storage.objects;
create policy foto_upload on storage.objects for insert to authenticated
  with check (bucket_id = 'fotografije');
drop policy if exists foto_read on storage.objects;
create policy foto_read on storage.objects for select using (bucket_id = 'fotografije');


-- 5) SEED: zgrada + 38 stanova + 68 stavki ---------------------
insert into zgrade (id, naziv, broj_stanova) values ('00000000-0000-0000-0000-000000000001','Zgrada 1', 38) on conflict do nothing;

insert into stanovi (zgrada_id, oznaka, redoslijed) values
('00000000-0000-0000-0000-000000000001','S-01',1),
('00000000-0000-0000-0000-000000000001','S-02',2),
('00000000-0000-0000-0000-000000000001','S-03',3),
('00000000-0000-0000-0000-000000000001','S-04',4),
('00000000-0000-0000-0000-000000000001','S-05',5),
('00000000-0000-0000-0000-000000000001','S-06',6),
('00000000-0000-0000-0000-000000000001','S-07',7),
('00000000-0000-0000-0000-000000000001','S-08',8),
('00000000-0000-0000-0000-000000000001','S-09',9),
('00000000-0000-0000-0000-000000000001','S-10',10),
('00000000-0000-0000-0000-000000000001','S-11',11),
('00000000-0000-0000-0000-000000000001','S-12',12),
('00000000-0000-0000-0000-000000000001','S-13',13),
('00000000-0000-0000-0000-000000000001','S-14',14),
('00000000-0000-0000-0000-000000000001','S-15',15),
('00000000-0000-0000-0000-000000000001','S-16',16),
('00000000-0000-0000-0000-000000000001','S-17',17),
('00000000-0000-0000-0000-000000000001','S-18',18),
('00000000-0000-0000-0000-000000000001','S-19',19),
('00000000-0000-0000-0000-000000000001','S-20',20),
('00000000-0000-0000-0000-000000000001','S-21',21),
('00000000-0000-0000-0000-000000000001','S-22',22),
('00000000-0000-0000-0000-000000000001','S-23',23),
('00000000-0000-0000-0000-000000000001','S-24',24),
('00000000-0000-0000-0000-000000000001','S-25',25),
('00000000-0000-0000-0000-000000000001','S-26',26),
('00000000-0000-0000-0000-000000000001','S-27',27),
('00000000-0000-0000-0000-000000000001','S-28',28),
('00000000-0000-0000-0000-000000000001','S-29',29),
('00000000-0000-0000-0000-000000000001','S-30',30),
('00000000-0000-0000-0000-000000000001','S-31',31),
('00000000-0000-0000-0000-000000000001','S-32',32),
('00000000-0000-0000-0000-000000000001','S-33',33),
('00000000-0000-0000-0000-000000000001','S-34',34),
('00000000-0000-0000-0000-000000000001','S-35',35),
('00000000-0000-0000-0000-000000000001','S-36',36),
('00000000-0000-0000-0000-000000000001','S-37',37),
('00000000-0000-0000-0000-000000000001','S-38',38)
on conflict (zgrada_id, oznaka) do nothing;

insert into stavke (id, prostorija, naziv, redoslijed) values
(1,'ULAZ / HODNIK','Ulazna vrata — bez ogrebotina, udubljenja, boja OK',1),
(2,'ULAZ / HODNIK','Ulazna vrata — brava, cilindar, 2 ključa rade',2),
(3,'ULAZ / HODNIK','Ulazna vrata — kvaka, špijunka, dihtung kompletan',3),
(4,'ULAZ / HODNIK','Ulazna vrata — štok poravnat, silikon/akril čist',4),
(5,'ULAZ / HODNIK','Vrata se zatvaraju bez taranja, ne škripe',5),
(6,'ULAZ / HODNIK','Prekidač i svjetlo u hodniku rade',6),
(7,'ULAZ / HODNIK','Interfon / video-interfon radi',7),
(8,'ULAZ / HODNIK','Razvodna tabla — označeni osigurači, poklopac',8),
(9,'ULAZ / HODNIK','Pod i sokle na ulazu bez oštećenja',9),
(10,'DNEVNA / TRPEZARIJA','Zidovi — glet ravan, bez pukotina/talasanja',10),
(11,'DNEVNA / TRPEZARIJA','Krečenje — bez fleka, ujednačeno, bez tragova valjka',11),
(12,'DNEVNA / TRPEZARIJA','Plafon — bez pukotina, fleka i prelaza',12),
(13,'DNEVNA / TRPEZARIJA','Parket/pod — bez ogrebotina, ne škripi, zazor uz zid',13),
(14,'DNEVNA / TRPEZARIJA','Sokle — postavljene, gerung uglovi, silikon čist',14),
(15,'DNEVNA / TRPEZARIJA','Sve utičnice rade (test) + maske ravne',15),
(16,'DNEVNA / TRPEZARIJA','Svi prekidači rade + maske poravnate',16),
(17,'DNEVNA / TRPEZARIJA','Plafonski priključak / rasvjeta OK',17),
(18,'DNEVNA / TRPEZARIJA','TV i internet priključak rade',18),
(19,'DNEVNA / TRPEZARIJA','Prozor — otvaranje/kip, okov podešen',19),
(20,'DNEVNA / TRPEZARIJA','Prozor — staklo bez ogrebotina/napukline',20),
(21,'DNEVNA / TRPEZARIJA','Prozor — dihtung ne propušta, klupica, silikon',21),
(22,'DNEVNA / TRPEZARIJA','Roletne — dižu/spuštaju, gurtna/motor radi',22),
(23,'KUHINJA','Voda topla/hladna — priključci bez curenja',23),
(24,'KUHINJA','Odvod / sifon priprema OK',24),
(25,'KUHINJA','Priključak za sudomašinu',25),
(26,'KUHINJA','Struja za ploču/šporet + napa',26),
(27,'KUHINJA','Utičnice iznad radne ploče rade',27),
(28,'KUHINJA','Zidne pločice — fuge, ravnoća, bez šupljih',28),
(29,'KUHINJA','Ventilacija / odvod nape',29),
(30,'SPAVAĆA SOBA','Zidovi i plafon — glet/krečenje bez fleka',30),
(31,'SPAVAĆA SOBA','Parket bez oštećenja + sokle',31),
(32,'SPAVAĆA SOBA','Sobna vrata — bez ogrebotina, ne taru pod',32),
(33,'SPAVAĆA SOBA','Sobna vrata — brava/kvaka, štok, gerung, ne škripe',33),
(34,'SPAVAĆA SOBA','Utičnice i prekidači rade',34),
(35,'SPAVAĆA SOBA','Rasvjeta priključak OK',35),
(36,'SPAVAĆA SOBA','Prozor — otvaranje, staklo, dihtung, roletna',36),
(37,'SPAVAĆA SOBA','Plakar/niša ako postoji — OK',37),
(38,'KUPATILO / WC','Zidne pločice — ravne, fuge ujednačene, bez šupljih',38),
(39,'KUPATILO / WC','Podne pločice — pad ka slivniku, fuge',39),
(40,'KUPATILO / WC','Silikon uglovi/oko kade-tuša — čist, bez plijesni',40),
(41,'KUPATILO / WC','WC šolja — pričvršćena, ne klima',41),
(42,'KUPATILO / WC','Vodokotlić — punjenje/ispiranje, bez curenja',42),
(43,'KUPATILO / WC','Umivaonik — pričvršćen, sifon, slavina, bez curenja',43),
(44,'KUPATILO / WC','Tuš/kada — slavina, ručka, crijevo, odvod',44),
(45,'KUPATILO / WC','Tuš kabina — staklo, zaptivka, vrata',45),
(46,'KUPATILO / WC','Slivnik — otiče, rešetka, vodeni zatvarač (miris)',46),
(47,'KUPATILO / WC','Bojler — radi, sig. ventil, bez curenja',47),
(48,'KUPATILO / WC','Ventilator/odvod radi',48),
(49,'KUPATILO / WC','Ogledalo / rasvjeta / utičnica (IP zaštita)',49),
(50,'KUPATILO / WC','Sušač peškira/radijator ako postoji',50),
(51,'KUPATILO / WC','Revizioni otvor / pristup instalacijama',51),
(52,'KUPATILO / WC','TEST CURENJA — 24h provjera bez kapanja',52),
(53,'TERASA / BALKON','Pločice — pad ka odvodu, fuge, bez pucanja',53),
(54,'TERASA / BALKON','Hidroizolacija — voda se ne zadržava',54),
(55,'TERASA / BALKON','Slivnik/odvod terase otiče',55),
(56,'TERASA / BALKON','Ograda — stabilna, visina, pričvršćenje',56),
(57,'TERASA / BALKON','Silikon spojevi + vrata terase (prag, dihtung)',57),
(58,'GRIJANJE (podno)','Termostat(i) rade — zagrijava ravnomjerno',58),
(59,'GRIJANJE (podno)','Razdjelnik dostupan i označen',59),
(60,'GRIJANJE (podno)','Nema hladnih zona / curenja (vodeno: pritisak drži)',60),
(61,'ZAVRŠNO / PREDAJA','Sva stakla i ogledala oprana',61),
(62,'ZAVRŠNO / PREDAJA','Pod opran — bez šuta, ljepila, boje',62),
(63,'ZAVRŠNO / PREDAJA','Naljepnice skinute (prozori, sanitarije, vrata)',63),
(64,'ZAVRŠNO / PREDAJA','Sve maske/utičnice komplet, ništa ne fali',64),
(65,'ZAVRŠNO / PREDAJA','Nema viška materijala u stanu',65),
(66,'ZAVRŠNO / PREDAJA','Brojila očitana i zapisana (struja/voda)',66),
(67,'ZAVRŠNO / PREDAJA','Ključevi kompletni i označeni',67),
(68,'ZAVRŠNO / PREDAJA','Garantni listovi + uputstva spremni',68)
on conflict (id) do update set prostorija=excluded.prostorija, naziv=excluded.naziv;
