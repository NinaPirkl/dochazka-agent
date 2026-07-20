# Docházka Agent

Automatické sestavení měsíčního výkazu z Jiry a odeslání do Jira Clockwork.

---

## Architektura

<img width="2720" height="2040" alt="dochazka_agent_architecture_pro" src="https://github.com/user-attachments/assets/229b3db0-190c-41c8-ad87-c829eb439689" />

---

## Jak spustit

Windows:

1. Stáhni repozitář jako ZIP → rozbal
2. Dvojklik na `spustit_agenta.bat`
3. Prohlížeč se otevře automaticky

Mac / Linux:

1. Stáhni repozitář jako ZIP → rozbal
2. V Terminálu (jednorázově): `chmod +x spustit_agenta.sh`
3. Spusť: `./spustit_agenta.sh`

> Python musí být nainstalovaný. Na Macu je předinstalovaný. Na Windows stáhni z [python.org](https://python.org).
> Agent běží lokálně na `http://localhost:8080` — lokální server (`server.py`) obchází CORS omezení Atlassianu.

---

## Použití

1. Zadej Jira email + [API token](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Vyber měsíc, zadej volné dny a přesčasy
3. Klikni **Načíst & analyzovat**
4. Zkontroluj návrh — tabulka je plně editovatelná (změna tasku, hodin, mazání, přidání záznamů)
5. **Odeslat do Clockwork** nebo **Stáhnout CSV**

### Co agent hlídá automaticky

- **Víkendy a české státní svátky** (včetně Velikonoc) — vynechány z rozvrhu
- **Duplicitní záznamy** — dny které už v Clockwork máš zalogované se automaticky přeskočí
- **Validace před odesláním** — součet hodin za den musí sedět (8h nebo zadaný přesčas), platné klíče tasků, platné hodnoty

---

## Kontext z Clauda (volitelné)

Pro přesnější rozvrh požádej Clauda v **projektovém chatu** na konci měsíce:

> *"Připrav kontext pro docházka-agent za [měsíc] [rok]. Vytvoř JSON s Jira tasky které jsem řešila ve formátu `{"entries":[{"day":1,"key":"OBS-123","hours":6}]}`. Rozděl dny realisticky na 2-3 tasky."*

Výsledný JSON vlož do pole **Kontext z Clauda** ve druhém kroku. Claude prohledá všechny konverzace projektu — více chatů za měsíc nevadí.

> ⚠️ Používej projektový chat, ne nový. V novém chatu Claude nemá přístup k historii projektu.

---

## Technické detaily

- HTML/JS frontend + malý Python proxy server (`server.py`, pouze standardní knihovna)
- API token žije pouze v paměti prohlížeče po dobu sezení, nikam se neukládá
- Server při startu provede diagnostiku (DNS, spojení s Jirou) — případné problémy vypíše do terminálu

---

*Autor: Nina Pirkl*
