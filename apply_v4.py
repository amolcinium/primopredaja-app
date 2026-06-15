#!/usr/bin/env python3
# v4 migracija — Construction Management moduli:
#   izvodjaci (direktorij), zadaci (radni nalozi), dnevnik (gradilište), stanovi.faza
# Primjenjuje se na ŽIVU bazu preko db_password (pooler). Idempotentno.
import psycopg2, sys

creds = {}
for line in open('.credentials.txt', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); creds[k.strip()] = v.strip()
ref = creds['project_ref']; pw = creds['db_password']

SQL = r"""
-- ===== IZVOĐAČI (podizvođači) =====
create table if not exists public.izvodjaci (
  id uuid primary key default gen_random_uuid(),
  ime text not null,
  struka text,
  telefon text,
  napomena text,
  created_at timestamptz default now()
);

-- ===== ZADACI (radni nalozi) =====
create table if not exists public.zadaci (
  id uuid primary key default gen_random_uuid(),
  stan_id uuid references public.stanovi(id) on delete set null,
  izvodjac_id uuid references public.izvodjaci(id) on delete set null,
  naziv text not null,
  opis text,
  prioritet text default 'Normalan' check (prioritet in ('Normalan','Visok','Kritičan')),
  rok date,
  status text default 'Otvoren' check (status in ('Otvoren','U toku','Završen','Otkazan')),
  foto text,
  autor text,
  created_at timestamptz default now(),
  datum_zavrsetka timestamptz
);

-- ===== DNEVNIK GRADILIŠTA =====
create table if not exists public.dnevnik (
  id uuid primary key default gen_random_uuid(),
  datum date not null default current_date,
  vrijeme text,        -- vremenske prilike
  ekipe text,          -- ko je radio
  uradjeno text,       -- šta je urađeno
  isporuke text,       -- materijal / isporuke
  problemi text,
  foto text,
  autor text,
  created_at timestamptz default now()
);

-- ===== FAZA radova po stanu =====
alter table public.stanovi add column if not exists faza text default 'Grubi radovi';

-- ===== RLS (authenticated full access, kao ostatak app-a) =====
do $$
declare t text;
begin
  foreach t in array array['izvodjaci','zadaci','dnevnik'] loop
    execute format('alter table public.%I enable row level security', t);
    if not exists (select 1 from pg_policies where schemaname='public' and tablename=t and policyname='auth_all') then
      execute format('create policy auth_all on public.%I for all to authenticated using (true) with check (true)', t);
    end if;
    if not exists (select 1 from pg_publication_tables where pubname='supabase_realtime' and schemaname='public' and tablename=t) then
      execute format('alter publication supabase_realtime add table public.%I', t);
    end if;
  end loop;
end $$;
"""

hosts = [
    ("aws-1-eu-central-1.pooler.supabase.com", 5432, f"postgres.{ref}"),
    ("aws-0-eu-central-1.pooler.supabase.com", 5432, f"postgres.{ref}"),
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
        cur.execute("select table_name from information_schema.tables where table_schema='public' and table_name in ('izvodjaci','zadaci','dnevnik') order by table_name;")
        tbls = [r[0] for r in cur.fetchall()]
        cur.execute("select column_name from information_schema.columns where table_name='stanovi' and column_name='faza';")
        faza = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
        print(f"OK via {host}")
        print("nove tabele:", tbls, "| stanovi.faza:", faza)
        sys.exit(0)
    except Exception as e:
        last = f"{host}: {type(e).__name__}: {str(e)[:120]}"
        print("  fail", last)
print("ALL HOSTS FAILED:", last); sys.exit(1)
