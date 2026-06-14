#!/usr/bin/env python3
# v3 migracija: poslovni prostor + kategorija stana + nove prostorije (ostava, kupatilo 2, fasada-klima)
# Primjenjuje se na ZIVU bazu preko db_password (pooler). Idempotentno.
import re, sys, psycopg2

creds = {}
for line in open('.credentials.txt', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        creds[k.strip()] = v.strip()

ref = creds['project_ref']
pw  = creds['db_password']

SQL = r"""
-- ===== v3 šema =====
alter table public.stanovi add column if not exists vrsta text not null default 'stan';   -- 'stan' | 'poslovni'
alter table public.stanovi add column if not exists kategorija text;                        -- Garsonjera/Jednosoban/Dvosoban/...
alter table public.stanovi add column if not exists opis text;                              -- slobodan opis
alter table public.stavke  add column if not exists vrsta text not null default 'stan';     -- 'stan' | 'poslovni' | 'sve'

-- ZAVRŠNO / PREDAJA mora ostati na kraju: 61-68 -> 90-97 (guard: samo ako još nije pomjereno)
update public.stavke set redoslijed = redoslijed + 29
 where prostorija = 'ZAVRŠNO / PREDAJA' and redoslijed between 61 and 68;

-- ===== nove STAN prostorije =====
insert into public.stavke (id, prostorija, naziv, redoslijed, primjenjivost, vrsta) values
 (100,'TERASA / BALKON','Fasada na balkonu kod klime — prefarbana/sanirana poslije montaže nosača',85,'sve','stan'),
 (101,'OSTAVA','Pod — obloga/estrih, bez oštećenja',69,'sve','stan'),
 (102,'OSTAVA','Zidovi i plafon — obrađeni, bez fleka',70,'sve','stan'),
 (103,'OSTAVA','Rasvjeta i prekidač rade',71,'sve','stan'),
 (104,'OSTAVA','Vrata ostave — brava/kvaka, ne taru pod',72,'sve','stan'),
 (105,'OSTAVA','Police / nosači (ako predviđeno)',73,'sve','stan'),
 (106,'KUPATILO 2 (MANJE)','Zidne pločice — ravne, fuge, bez šupljih',74,'sve','stan'),
 (107,'KUPATILO 2 (MANJE)','Podne pločice — pad ka slivniku, fuge',75,'sve','stan'),
 (108,'KUPATILO 2 (MANJE)','Silikon uglovi — čist, bez plijesni',76,'sve','stan'),
 (109,'KUPATILO 2 (MANJE)','WC šolja — pričvršćena, ne klima',77,'sve','stan'),
 (110,'KUPATILO 2 (MANJE)','Vodokotlić — punjenje/ispiranje, bez curenja',78,'sve','stan'),
 (111,'KUPATILO 2 (MANJE)','Umivaonik — sifon, slavina, bez curenja',79,'sve','stan'),
 (112,'KUPATILO 2 (MANJE)','Tuš/kada — slavina, crijevo, odvod',80,'sve','stan'),
 (113,'KUPATILO 2 (MANJE)','Slivnik — otiče, vodeni zatvarač (miris)',81,'sve','stan'),
 (114,'KUPATILO 2 (MANJE)','Ventilator/odvod radi',82,'sve','stan'),
 (115,'KUPATILO 2 (MANJE)','Ogledalo/rasvjeta/utičnica (IP zaštita)',83,'sve','stan')
on conflict (id) do nothing;

-- ===== POSLOVNI PROSTOR checklista (vrsta='poslovni') =====
insert into public.stavke (id, prostorija, naziv, redoslijed, primjenjivost, vrsta) values
 (120,'ULAZ I IZLOG','Ulazna vrata / portal — montaža, zaptivanje, brava + ključevi',120,'sve','poslovni'),
 (121,'ULAZ I IZLOG','Izlog / staklena fasada — staklo bez oštećenja, zaptiveno',121,'sve','poslovni'),
 (122,'ULAZ I IZLOG','Sigurnosna roletna / rešetka — funkcija (ako postoji)',122,'sve','poslovni'),
 (123,'ULAZ I IZLOG','Mjesto za reklamu / natpis pripremljeno',123,'sve','poslovni'),
 (124,'PROSTOR','Pod — završna obloga položena, ravna, bez oštećenja',124,'sve','poslovni'),
 (125,'PROSTOR','Sokl / lajsne postavljene',125,'sve','poslovni'),
 (126,'PROSTOR','Zidovi — gletovani/obojeni, bez pukotina',126,'sve','poslovni'),
 (127,'PROSTOR','Plafon — obrađen / spušteni plafon ravan',127,'sve','poslovni'),
 (128,'PROSTOR','Unutrašnje pregrade / vrata (ako ima)',128,'sve','poslovni'),
 (129,'ELEKTROINSTALACIJE','Razvodna tabla — osigurači označeni, FID test',129,'sve','poslovni'),
 (130,'ELEKTROINSTALACIJE','Utičnice — broj i raspored, funkcija',130,'sve','poslovni'),
 (131,'ELEKTROINSTALACIJE','Rasvjeta — sva svjetla rade',131,'sve','poslovni'),
 (132,'ELEKTROINSTALACIJE','Slaba struja — internet/telefon/alarm pripremljeno',132,'sve','poslovni'),
 (133,'ELEKTROINSTALACIJE','Brojilo struje — očitano, prepisano na korisnika',133,'sve','poslovni'),
 (134,'VODOVOD I SANITARIJE','WC — šolja, vodokotlić, funkcija',134,'sve','poslovni'),
 (135,'VODOVOD I SANITARIJE','Lavabo / slavina — bez curenja',135,'sve','poslovni'),
 (136,'VODOVOD I SANITARIJE','Bojler / topla voda (ako ima)',136,'sve','poslovni'),
 (137,'VODOVOD I SANITARIJE','Odvod / sifoni — protočnost, bez mirisa',137,'sve','poslovni'),
 (138,'VODOVOD I SANITARIJE','Brojilo vode — očitano',138,'sve','poslovni'),
 (139,'GRIJANJE / KLIMA','Klima/grijanje jedinica — montirana, grije i hladi',139,'sve','poslovni'),
 (140,'GRIJANJE / KLIMA','Fasada oko nosača klime — sanirana/prefarbana',140,'sve','poslovni'),
 (141,'GRIJANJE / KLIMA','Ventilacija / odsis (san. čvor) — funkcija',141,'sve','poslovni'),
 (142,'ZAVRŠNO / PREDAJA','Završno čišćenje — prostor i izlog očišćeni, otpad uklonjen',142,'sve','poslovni'),
 (143,'ZAVRŠNO / PREDAJA','Ključevi — broj predanih ključeva evidentiran',143,'sve','poslovni'),
 (144,'ZAVRŠNO / PREDAJA','Zapisnik o primopredaji + brojila potpisani',144,'sve','poslovni')
on conflict (id) do nothing;
"""

hosts = [
    ("aws-0-eu-central-1.pooler.supabase.com", 5432, f"postgres.{ref}"),
    ("aws-1-eu-central-1.pooler.supabase.com", 5432, f"postgres.{ref}"),
    (f"db.{ref}.supabase.co", 5432, "postgres"),
]
last = None
for host, port, user in hosts:
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=pw,
                                dbname="postgres", sslmode="require", connect_timeout=15)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(SQL)
        cur.execute("select vrsta, count(*) from public.stavke group by vrsta order by vrsta;")
        rows = cur.fetchall()
        cur.execute("select column_name from information_schema.columns where table_name='stanovi' and column_name in ('vrsta','kategorija','opis') order by column_name;")
        cols = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
        print(f"OK via {host}")
        print("stavke po vrsti:", rows)
        print("nove stanovi kolone:", cols)
        sys.exit(0)
    except Exception as e:
        last = f"{host}: {type(e).__name__}: {str(e)[:120]}"
        print("  fail", last)
print("ALL HOSTS FAILED:", last)
sys.exit(1)
