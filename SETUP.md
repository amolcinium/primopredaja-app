# Primopredaja — web app · postavljanje (≈15 min)

Mobilni alat za praćenje završnih radova i dorada. Single-file app (`index.html`) + Supabase baza.

## Šta dobiješ
- 📊 **Pregled** — KPI objekta (% završeno, spremni, otvorene/kritične dorade)
- 🏢 **Stanovi** — 38 stanova, % po stanu, „Spreman?", tap → checklista po prostorijama (68 detalja)
- 🛠️ **Dorade** — automatski se otvaraju kad označiš **✗**, zatvaraju kad označiš **OK** (server-side triger), foto prije/poslije s telefona, rok + alarm za probijen rok
- Login na **jedan zajednički kod**
- **⚙️ Admin** u app-u — naziv zgrade, dodavanje/brisanje stanova, promjena ključeva (bez diranja baze)

---

## Korak 1 — Napravi Supabase projekat
1. https://supabase.com → **New project** → ime `primopredaja`, izaberi region (Frankfurt), lozinka baze.
2. Sačekaj ~2 min da se digne.

## Korak 2 — Pokreni bazu
1. U projektu: **SQL Editor → New query**.
2. Otvori `migracija.sql`, kopiraj **cijeli sadržaj**, nalijepi → **Run**.
3. Treba da javi success (kreira tabele, triger, RLS, 38 stanova, 68 stavki, storage bucket).

## Korak 3 — Napravi pristupni nalog (= zajednički kod)
1. **Authentication → Users → Add user → Create new user**.
2. Email: `ekipa@primopredaja.local`  ·  Password: **TVOJ KOD** (npr. `Ulcinj2026`).
3. Uključi **Auto Confirm User** (da ne traži email potvrdu). Create.
> Taj password je pristupni kod koji daješ radnicima. Promjena koda = promijeni password ovdje.

## Korak 4 — Objavi (izaberi jedno)
> NE moraš editovati `index.html` — ključeve unosiš u samoj aplikaciji (ekran „Podešavanje").
- **Najlakše — Cloudflare Pages:** dashboard → Pages → *Upload assets* → prevuci `index.html` → deploy. Dobiješ link tipa `primopredaja.pages.dev`. (Po želji veži subdomenu `primopredaja.ulcinno.me`.)
- **Test lokalno:** `python3 -m http.server` pa otvori `localhost:8000`.

## Korak 5 — Unesi ključeve (jednom, u app-u)
1. Otvori app → pojavi se ekran **Podešavanje**.
2. Iz Supabase **Settings → API** prekopiraj **Project URL** + **anon public** ključ, nalijepi u app, sačuvaj.
3. Čuva se u browseru (localStorage). Kasnije promjena: dugme **⚙️ → Promijeni Supabase ključeve**.

## Korak 6 — Probaj
1. Otvori link na telefonu → unesi kod → uđi.
2. Stanovi → S-01 → tapni stavku → **✗ Nije u redu** → dorada se sama pojavi u tabu Dorade.
3. U Dorade dodaj izvođača, rok, foto. Kad popraviš → na stavci stavi **OK** → dorada se sama zatvori.

---

## Sigurnost / napomene
- `anon` ključ je javan (normalno) — pristup štiti RLS: bez prijave (koda) nema podataka.
- Foto bucket je `public` (lakše dijeljenje linka). Ako želiš privatne slike, javi pa prebacimo na potpisane URL-ove.
- Svako može upisati ime u polje „Tvoje ime" za djelimičnu atribuciju (pošto je login zajednički).
- Promjena broja stanova / dodavanje zgrada: kroz Supabase tabele `stanovi` / `zgrade` (ili javi za admin ekran).

## Sljedeći koraci (opciono)
- Pravi nalozi po osobi (umjesto zajedničkog koda) + tačan audit „ko je šta"
- Zapisnik o primopredaji (PDF: brojila, ključevi, potpisi)
- Izvještaj po izvođaču (prosječno vrijeme zatvaranja dorade)
- Realni podaci stanova (spratovi/kvadrature/tip grijanja) — pošalji spisak
