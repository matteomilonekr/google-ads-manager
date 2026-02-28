# Google Ads MCP Server

Un server MCP (Model Context Protocol) per la gestione completa di Google Ads tramite Claude e altri assistenti AI compatibili con MCP. Costruito con [FastMCP](https://github.com/jlowin/fastmcp) e le [Google Ads API](https://developers.google.com/google-ads/api/docs/start) ufficiali.

## Funzionalita

**55 tool** che coprono l'intero workflow Google Ads: lettura dati performance, creazione campagne, gestione keyword, upload conversioni e molto altro.

### Tool di Lettura (29)

| Tool | Descrizione |
|------|-------------|
| `get_account_overview` | Riepilogo performance a livello account |
| `list_campaigns` | Lista campagne con filtri stato/tipo |
| `get_campaign_performance` | Metriche campagne su intervallo date |
| `list_ad_groups` | Lista gruppi annunci con filtri campagna/stato |
| `get_ad_group_performance` | Metriche gruppi annunci su intervallo date |
| `gads_list_ad_group_ads` | Lista annunci con dettagli creativi, performance e stato policy |
| `list_keywords` | Lista keyword con tipi di corrispondenza e offerte |
| `get_keyword_performance` | Metriche keyword su intervallo date |
| `search_terms_report` | Termini di ricerca che attivano gli annunci |
| `gads_list_labels` | Etichette dell'account |
| `gads_list_campaign_labels` | Associazioni campagna-etichetta |
| `gads_list_ad_group_labels` | Associazioni gruppo annunci-etichetta |
| `gads_list_ad_group_ad_labels` | Associazioni annuncio-etichetta |
| `gads_list_ad_group_criterion_labels` | Associazioni criterio-etichetta |
| `gads_list_customer_labels` | Associazioni cliente-etichetta |
| `gads_list_audiences` | Segmenti di pubblico e performance |
| `gads_list_user_interests` | Categorie di interessi utente |
| `gads_list_campaign_budgets` | Configurazione e spesa budget |
| `gads_get_bidding_strategies` | Strategie di offerta campagne |
| `gads_get_ad_group_bidding_strategies` | Strategie di offerta gruppi annunci |
| `gads_list_change_history` | Cronologia modifiche entita account |
| `gads_list_customer_clients` | Gerarchia account cliente |
| `gads_list_accessible_customers` | Account cliente accessibili |
| `gads_list_merchant_center_links` | Account Merchant Center collegati |
| `gads_geographic_view` | Dati performance per localita |
| `gads_shopping_performance_view` | Performance Shopping a livello prodotto |
| `gads_display_keyword_view` | Performance keyword display |
| `gads_topic_view` | Performance targeting per argomento |
| `gads_user_location_view` | Performance per posizione fisica utente |
| `gads_click_view` | Dati a livello click con GCLID e dispositivo |
| `gads_generate_keyword_ideas` | Idee keyword da seed o URL |
| `gads_execute_gaql` | Esecuzione query GAQL personalizzate |

### Tool di Scrittura (26)

| Tool | Descrizione |
|------|-------------|
| `gads_create_campaign` | Creazione campagne con budget e offerta |
| `gads_update_campaign` | Aggiornamento impostazioni campagna |
| `gads_set_campaign_status` | Attivazione, pausa o rimozione campagne |
| `gads_create_ad_group` | Creazione gruppi annunci nelle campagne |
| `gads_set_ad_group_status` | Attivazione, pausa o rimozione gruppi annunci |
| `gads_set_ad_status` | Attivazione, pausa o rimozione annunci |
| `gads_add_keywords` | Aggiunta keyword con tipi di corrispondenza e offerte |
| `gads_update_keyword` | Aggiornamento offerte o stato keyword |
| `gads_add_negative_keywords` | Aggiunta keyword negative (campagna o gruppo annunci) |
| `gads_create_responsive_search_ad` | Creazione RSA con titoli/descrizioni multipli |
| `gads_create_responsive_display_ad` | Creazione annunci display responsive |
| `gads_create_demand_gen_ad` | Creazione annunci Demand Gen |
| `gads_create_video_ad` | Creazione annunci video (YouTube) |
| `gads_update_budget` | Aggiornamento importo budget campagna |
| `gads_set_bidding_strategy` | Impostazione o modifica strategia di offerta |
| `gads_create_ad_extension` | Creazione sitelink, callout, estensioni di chiamata |
| `gads_set_location_targeting` | Targeting geografico per localita |
| `gads_set_language_targeting` | Targeting per lingua |
| `gads_set_device_targeting` | Modificatori offerta per dispositivo |
| `gads_set_demographic_targeting` | Targeting per eta, genere, reddito |
| `gads_create_audience_segment` | Creazione segmenti di pubblico personalizzati |
| `gads_create_asset` | Creazione asset riutilizzabili (immagini, testo, video) |
| `gads_create_asset_group` | Creazione gruppi di asset per Performance Max |
| `gads_add_asset_group_assets` | Collegamento asset ai gruppi di asset |
| `gads_set_listing_group_filter` | Filtri gruppi schede prodotto (Shopping) |
| `gads_link_merchant_center` | Collegamento account Merchant Center |
| `gads_upload_click_conversions` | Upload conversioni click offline |
| `gads_upload_customer_list` | Upload liste clienti per customer match |
| `gads_remove_customer_list_members` | Rimozione membri dalle liste clienti |

## Prerequisiti

- Python 3.12+
- Account sviluppatore Google Ads con accesso API
- Credenziali OAuth2 (client ID, client secret, refresh token)
- Token sviluppatore Google Ads

## Dipendenze

| Pacchetto | Versione | Descrizione |
|-----------|----------|-------------|
| `mcp` | >= 1.0.0 | Framework Model Context Protocol (FastMCP) |
| `google-ads` | >= 25.0.0 | Client ufficiale Google Ads API |
| `pydantic` | >= 2.0.0 | Validazione dati e modelli input |
| `httpx` | >= 0.27.0 | Client HTTP asincrono |
| `python-dotenv` | >= 1.0.0 | Caricamento variabili d'ambiente da file `.env` |

### Dipendenze di sviluppo (opzionali)

| Pacchetto | Versione | Descrizione |
|-----------|----------|-------------|
| `pytest` | >= 8.0.0 | Framework di test |
| `pytest-asyncio` | >= 0.23.0 | Supporto test asincroni |
| `pytest-cov` | >= 4.0.0 | Copertura codice |

## Installazione

```bash
# Clona il repository
git clone <repo-url>
cd google-ads-manager

# Installa con uv (consigliato)
uv sync

# Oppure con pip
pip install -e .

# Con dipendenze di sviluppo
uv sync --extra dev
# oppure
pip install -e ".[dev]"
```

## Configurazione

Imposta le seguenti variabili d'ambiente (o aggiungile a un file `.env`):

```bash
# Obbligatorie
GOOGLE_ADS_DEVELOPER_TOKEN=il_tuo_developer_token
GOOGLE_ADS_CLIENT_ID=il_tuo_client_id
GOOGLE_ADS_CLIENT_SECRET=il_tuo_client_secret
GOOGLE_ADS_REFRESH_TOKEN=il_tuo_refresh_token

# Opzionale — necessario per account MCC (manager)
GOOGLE_ADS_LOGIN_CUSTOMER_ID=il_tuo_id_account_manager
```

## Utilizzo

### Avviare il server

```bash
uv run python -m google_ads_mcp.server
```

### Configurazione Claude Desktop / Claude Code

Aggiungi alle impostazioni MCP:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/matteomilonekr/google-ads-manager.git", "google-ads-mcp"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "il_tuo_developer_token",
        "GOOGLE_ADS_CLIENT_ID": "il_tuo_client_id",
        "GOOGLE_ADS_CLIENT_SECRET": "il_tuo_client_secret",
        "GOOGLE_ADS_REFRESH_TOKEN": "il_tuo_refresh_token",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "il_tuo_id_account_manager"
      }
    }
  }
}
```

Non serve clonare il repository: `uvx` scarica e installa direttamente da GitHub.

## Struttura del Progetto

```
google_ads_mcp/
├── server.py              # Server FastMCP con gestione lifecycle
├── auth.py                # Autenticazione OAuth2 e creazione client
├── client.py              # Wrapper client Google Ads API
├── models/
│   ├── common.py          # Enum condivisi, validatori, modelli base
│   ├── tool_inputs.py     # Modelli input per tool di lettura
│   ├── mutation_inputs.py # Modelli input per tool di scrittura
│   ├── creation_inputs.py # Modelli input per operazioni di creazione
│   └── asset_inputs.py    # Modelli input per operazioni asset
├── tools/
│   ├── _helpers.py        # Utility condivise (mappe stato, cast sicuri)
│   ├── account.py         # Panoramica account
│   ├── ads.py             # Annunci (creativita, policy, performance)
│   ├── ad_groups.py       # Lista e performance gruppi annunci
│   ├── audiences.py       # Pubblico e interessi utente
│   ├── budgets.py         # Budget, strategie offerta, cronologia modifiche
│   ├── campaigns.py       # Lista e performance campagne
│   ├── gaql.py            # Esecuzione query GAQL personalizzate
│   ├── hierarchy.py       # Gerarchia account, clienti e Merchant Center
│   ├── keyword_planner.py # Generazione idee keyword
│   ├── keywords.py        # Lista e performance keyword
│   ├── labels.py          # Tutti i tipi di etichette
│   ├── search_terms.py    # Report termini di ricerca
│   ├── views.py           # Viste geografiche, shopping, display, argomenti, click
│   └── mutations/
│       ├── ad_group_ops.py    # Operazioni stato gruppi annunci
│       ├── ad_ops.py          # Operazioni stato annunci
│       ├── asset_ops.py       # Gestione asset e gruppi di asset
│       ├── bidding_ops.py     # Operazioni strategie di offerta
│       ├── budget_ops.py      # Operazioni aggiornamento budget
│       ├── campaign_ops.py    # Aggiornamento e stato campagne
│       ├── conversion_ops.py  # Upload conversioni offline
│       ├── creation_ops.py    # Creazione campagne, gruppi annunci e annunci
│       ├── customer_list_ops.py # Operazioni liste clienti
│       ├── extension_ops.py   # Creazione estensioni annuncio
│       ├── keyword_ops.py     # Aggiunta/aggiornamento/negative keyword
│       ├── shopping_ops.py    # Operazioni Shopping e Merchant Center
│       ├── targeting_ops.py   # Targeting localita, dispositivo, demografico
│       └── video_ops.py       # Creazione annunci video
├── builders/              # Builder per query GAQL e operazioni mutation
└── utils/
    ├── errors.py          # Classi eccezioni personalizzate
    ├── formatting.py      # Formattazione tabelle markdown, conversione valuta
    └── pagination.py      # Utility paginazione risultati
```

## Sviluppo

```bash
# Installa dipendenze di sviluppo
uv sync --extra dev

# Esegui i test
uv run --extra dev pytest tests/ -v

# Esegui un file di test specifico
uv run --extra dev pytest tests/test_tools_ads.py -v

# Esegui con copertura
uv run --extra dev pytest tests/ --cov=google_ads_mcp --cov-report=term-missing
```

### Suite di Test

655 test che coprono tutti i tool, modelli, builder e utility.

## Licenza

Proprietary. Tutti i diritti riservati. Questo software e concesso in licenza esclusivamente per uso personale. Non e consentito modificare, distribuire, sublicenziare o creare opere derivate da questo software senza autorizzazione scritta preventiva.
