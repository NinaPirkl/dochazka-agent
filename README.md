# Docházka Agent

Automatické sestavení měsíčního výkazu z Jiry a odeslání do Jira Clockwork.

**→ [Otevřít agenta](https://ninapirkl.github.io/dochazka-agent/dochazka_agent.html)**

---

## Architektura

<img width="2720" height="2040" alt="dochazka_agent_architecture_pro" src="https://github.com/user-attachments/assets/229b3db0-190c-41c8-ad87-c829eb439689" />

---

## Jak začít

1. Zadej Jira email + [API token](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Vyber měsíc, zadej volné dny a přesčasy
3. Klikni **Načíst & analyzovat**
4. Zkontroluj návrh, uprav pokud potřeba
5. **Odeslat do Clockwork** nebo **Stáhnout CSV**

---

## Kontext z Clauda (volitelné)

Pro přesnější rozvrh požádej Clauda v **projektovém chatu** na konci měsíce:

> *"Připrav kontext pro docházka-agent za [měsíc] [rok]. Vytvoř JSON s Jira tasky které jsem řešila ve formátu `{"entries":[{"day":1,"key":"OBS-123","hours":6}]}`"*

Výsledný JSON vlož do pole **Kontext z Clauda** ve druhém kroku. Claude prohledá všechny konverzace projektu — více chatů za měsíc nevadí.

> ⚠️ Používej projektový chat, ne nový. V novém chatu Claude nemá přístup k historii projektu.

---

## Technické detaily

- Čistý HTML/JS — bez závislostí, bez serveru
- API token žije pouze v paměti prohlížeče, nikam se neposílá

---

*Autor: Nina Pirkl*
