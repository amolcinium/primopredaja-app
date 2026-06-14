# -*- coding: utf-8 -*-
"""Generiše migracija.sql za Supabase (schema + RLS + trigger + seed 38 stanova + 68 stavki)."""

ITEMS = [
 ("ULAZ / HODNIK","Ulazna vrata — bez ogrebotina, udubljenja, boja OK"),
 ("ULAZ / HODNIK","Ulazna vrata — brava, cilindar, 2 ključa rade"),
 ("ULAZ / HODNIK","Ulazna vrata — kvaka, špijunka, dihtung kompletan"),
 ("ULAZ / HODNIK","Ulazna vrata — štok poravnat, silikon/akril čist"),
 ("ULAZ / HODNIK","Vrata se zatvaraju bez taranja, ne škripe"),
 ("ULAZ / HODNIK","Prekidač i svjetlo u hodniku rade"),
 ("ULAZ / HODNIK","Interfon / video-interfon radi"),
 ("ULAZ / HODNIK","Razvodna tabla — označeni osigurači, poklopac"),
 ("ULAZ / HODNIK","Pod i sokle na ulazu bez oštećenja"),
 ("DNEVNA / TRPEZARIJA","Zidovi — glet ravan, bez pukotina/talasanja"),
 ("DNEVNA / TRPEZARIJA","Krečenje — bez fleka, ujednačeno, bez tragova valjka"),
 ("DNEVNA / TRPEZARIJA","Plafon — bez pukotina, fleka i prelaza"),
 ("DNEVNA / TRPEZARIJA","Parket/pod — bez ogrebotina, ne škripi, zazor uz zid"),
 ("DNEVNA / TRPEZARIJA","Sokle — postavljene, gerung uglovi, silikon čist"),
 ("DNEVNA / TRPEZARIJA","Sve utičnice rade (test) + maske ravne"),
 ("DNEVNA / TRPEZARIJA","Svi prekidači rade + maske poravnate"),
 ("DNEVNA / TRPEZARIJA","Plafonski priključak / rasvjeta OK"),
 ("DNEVNA / TRPEZARIJA","TV i internet priključak rade"),
 ("DNEVNA / TRPEZARIJA","Prozor — otvaranje/kip, okov podešen"),
 ("DNEVNA / TRPEZARIJA","Prozor — staklo bez ogrebotina/napukline"),
 ("DNEVNA / TRPEZARIJA","Prozor — dihtung ne propušta, klupica, silikon"),
 ("DNEVNA / TRPEZARIJA","Roletne — dižu/spuštaju, gurtna/motor radi"),
 ("KUHINJA","Voda topla/hladna — priključci bez curenja"),
 ("KUHINJA","Odvod / sifon priprema OK"),
 ("KUHINJA","Priključak za sudomašinu"),
 ("KUHINJA","Struja za ploču/šporet + napa"),
 ("KUHINJA","Utičnice iznad radne ploče rade"),
 ("KUHINJA","Zidne pločice — fuge, ravnoća, bez šupljih"),
 ("KUHINJA","Ventilacija / odvod nape"),
 ("SPAVAĆA SOBA","Zidovi i plafon — glet/krečenje bez fleka"),
 ("SPAVAĆA SOBA","Parket bez oštećenja + sokle"),
 ("SPAVAĆA SOBA","Sobna vrata — bez ogrebotina, ne taru pod"),
 ("SPAVAĆA SOBA","Sobna vrata — brava/kvaka, štok, gerung, ne škripe"),
 ("SPAVAĆA SOBA","Utičnice i prekidači rade"),
 ("SPAVAĆA SOBA","Rasvjeta priključak OK"),
 ("SPAVAĆA SOBA","Prozor — otvaranje, staklo, dihtung, roletna"),
 ("SPAVAĆA SOBA","Plakar/niša ako postoji — OK"),
 ("KUPATILO / WC","Zidne pločice — ravne, fuge ujednačene, bez šupljih"),
 ("KUPATILO / WC","Podne pločice — pad ka slivniku, fuge"),
 ("KUPATILO / WC","Silikon uglovi/oko kade-tuša — čist, bez plijesni"),
 ("KUPATILO / WC","WC šolja — pričvršćena, ne klima"),
 ("KUPATILO / WC","Vodokotlić — punjenje/ispiranje, bez curenja"),
 ("KUPATILO / WC","Umivaonik — pričvršćen, sifon, slavina, bez curenja"),
 ("KUPATILO / WC","Tuš/kada — slavina, ručka, crijevo, odvod"),
 ("KUPATILO / WC","Tuš kabina — staklo, zaptivka, vrata"),
 ("KUPATILO / WC","Slivnik — otiče, rešetka, vodeni zatvarač (miris)"),
 ("KUPATILO / WC","Bojler — radi, sig. ventil, bez curenja"),
 ("KUPATILO / WC","Ventilator/odvod radi"),
 ("KUPATILO / WC","Ogledalo / rasvjeta / utičnica (IP zaštita)"),
 ("KUPATILO / WC","Sušač peškira/radijator ako postoji"),
 ("KUPATILO / WC","Revizioni otvor / pristup instalacijama"),
 ("KUPATILO / WC","TEST CURENJA — 24h provjera bez kapanja"),
 ("TERASA / BALKON","Pločice — pad ka odvodu, fuge, bez pucanja"),
 ("TERASA / BALKON","Hidroizolacija — voda se ne zadržava"),
 ("TERASA / BALKON","Slivnik/odvod terase otiče"),
 ("TERASA / BALKON","Ograda — stabilna, visina, pričvršćenje"),
 ("TERASA / BALKON","Silikon spojevi + vrata terase (prag, dihtung)"),
 ("GRIJANJE (podno)","Termostat(i) rade — zagrijava ravnomjerno"),
 ("GRIJANJE (podno)","Razdjelnik dostupan i označen"),
 ("GRIJANJE (podno)","Nema hladnih zona / curenja (vodeno: pritisak drži)"),
 ("ZAVRŠNO / PREDAJA","Sva stakla i ogledala oprana"),
 ("ZAVRŠNO / PREDAJA","Pod opran — bez šuta, ljepila, boje"),
 ("ZAVRŠNO / PREDAJA","Naljepnice skinute (prozori, sanitarije, vrata)"),
 ("ZAVRŠNO / PREDAJA","Sve maske/utičnice komplet, ništa ne fali"),
 ("ZAVRŠNO / PREDAJA","Nema viška materijala u stanu"),
 ("ZAVRŠNO / PREDAJA","Brojila očitana i zapisana (struja/voda)"),
 ("ZAVRŠNO / PREDAJA","Ključevi kompletni i označeni"),
 ("ZAVRŠNO / PREDAJA","Garantni listovi + uputstva spremni"),
]

def esc(s): return s.replace("'", "''")

sql = []
sql.append("""-- ============================================================
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
""")

# 5) SEED
sql.append("\n-- 5) SEED: zgrada + 38 stanova + 68 stavki ---------------------")
sql.append("insert into zgrade (id, naziv, broj_stanova) values "
           "('00000000-0000-0000-0000-000000000001','Zgrada 1', 38) on conflict do nothing;")

sql.append("\ninsert into stanovi (zgrada_id, oznaka, redoslijed) values")
vals = []
for i in range(1, 39):
    vals.append("('00000000-0000-0000-0000-000000000001','S-%02d',%d)" % (i, i))
sql.append(",\n".join(vals) + "\non conflict (zgrada_id, oznaka) do nothing;")

sql.append("\ninsert into stavke (id, prostorija, naziv, redoslijed) values")
vals = []
for idx, (pros, naz) in enumerate(ITEMS, 1):
    vals.append("(%d,'%s','%s',%d)" % (idx, esc(pros), esc(naz), idx))
sql.append(",\n".join(vals) + "\non conflict (id) do update set prostorija=excluded.prostorija, naziv=excluded.naziv;")

out = "/mnt/c/PlatformWeb/primopredaja-app/migracija.sql"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(sql) + "\n")
print("OK ->", out, "| stavki:", len(ITEMS))
