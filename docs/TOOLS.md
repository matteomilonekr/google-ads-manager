# Google Ads MCP Server — Catalogo Tool

> **55 tool** per la gestione completa di Google Ads tramite assistenti AI.
> Costruito su MCP (Model Context Protocol) + Google Ads API v18.

---

## Panoramica

| Categoria | Quantita |
|-----------|----------|
| Lettura — Account e Campagne | 7 |
| Lettura — Annunci, Keyword e Termini di Ricerca | 6 |
| Lettura — Etichette | 6 |
| Lettura — Pubblico e Interessi | 2 |
| Lettura — Budget, Offerte e Cronologia | 4 |
| Lettura — Gerarchia Account e Merchant Center | 3 |
| Lettura — Viste Performance | 5 |
| Lettura — Keyword Planner e GAQL | 2 |
| Scrittura — Gestione Campagne | 5 |
| Scrittura — Gestione Gruppi Annunci e Annunci | 5 |
| Scrittura — Keyword | 3 |
| Scrittura — Creazione Annunci (Avanzata) | 3 |
| Scrittura — Targeting | 5 |
| Scrittura — Asset e Shopping | 5 |
| Scrittura — Conversioni e Liste Clienti | 3 |
| **Totale** | **55** |

---

## Tool di Lettura (29)

### Account e Campagne

#### `get_account_overview`
Panoramica ad alto livello dell'account Google Ads con metriche chiave.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads (es. `1234567890` o `123-456-7890`) |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `response_format` | No | `markdown` o `json` |

---

#### `list_campaigns`
Lista campagne Google Ads con filtri opzionali per stato e tipo.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `status` | No | Filtro: `all`, `enabled`, `paused`, `removed` |
| `campaign_type` | No | Filtro: `all`, `search`, `display`, `shopping`, `video`, `performance_max`, `demand_gen`, `app`, `smart`, `hotel`, `local`, `local_services`, `travel` |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `get_campaign_performance`
Metriche performance campagne su intervallo date.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | ID campagna specifico |
| `status` | No | Filtro: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

**Metriche restituite:** Impressioni, Click, Costo, Conversioni, CTR, CPC medio, Tasso di conversione

---

#### `list_ad_groups`
Lista gruppi annunci con filtri opzionali per campagna e stato.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `status` | No | Filtro: `all`, `enabled`, `paused`, `removed` |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `get_ad_group_performance`
Metriche performance gruppi annunci su intervallo date.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `ad_group_id` | No | ID gruppo annunci specifico |
| `status` | No | Filtro: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

**Metriche restituite:** Impressioni, Click, Costo, Conversioni, CTR, CPC medio, Tasso di conversione

---

### Annunci, Keyword e Termini di Ricerca

#### `gads_list_ad_group_ads`
Lista annunci nei gruppi annunci con dettagli creativi, metriche performance e stato policy.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `ad_group_id` | No | Filtro per ID gruppo annunci |
| `status` | No | Filtro: `all`, `enabled`, `paused`, `removed` |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

**Campi restituiti:** ID Annuncio, Nome, Tipo, Stato, Stato Approvazione, Stato Revisione, Gruppo Annunci, Campagna, Impressioni, Click, Costo, Conversioni, CTR

---

#### `list_keywords`
Lista keyword con filtri opzionali per campagna e gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `ad_group_id` | No | Filtro per ID gruppo annunci |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `get_keyword_performance`
Metriche performance keyword su intervallo date.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `ad_group_id` | No | Filtro per ID gruppo annunci |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max 1-1000 (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `search_terms_report`
Report termini di ricerca che mostrano le query effettive che hanno attivato gli annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `ad_group_id` | No | Filtro per ID gruppo annunci |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max 1-5000 (default: 100) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

### Etichette

#### `gads_list_labels`
Lista tutte le etichette dell'account Google Ads.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_campaign_labels`
Lista associazioni campagna-etichetta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `label_id` | No | Filtro per ID etichetta |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_ad_group_labels`
Lista associazioni gruppo annunci-etichetta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | No | Filtro per ID gruppo annunci |
| `label_id` | No | Filtro per ID etichetta |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_ad_group_ad_labels`
Lista associazioni annuncio-etichetta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `label_id` | No | Filtro per ID etichetta |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_ad_group_criterion_labels`
Lista associazioni criterio-etichetta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `label_id` | No | Filtro per ID etichetta |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_customer_labels`
Lista associazioni cliente-etichetta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

### Pubblico e Interessi

#### `gads_list_audiences`
Lista segmenti di pubblico con info targeting e metriche performance.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_user_interests`
Lista categorie di interessi utente disponibili per il targeting.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `taxonomy_type` | No | Filtro per tipo tassonomia |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

### Budget, Offerte e Cronologia

#### `gads_list_campaign_budgets`
Lista budget campagne con configurazione dettagliata.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_get_bidding_strategies`
Configurazione strategie di offerta a livello campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_get_ad_group_bidding_strategies`
Informazioni offerte a livello gruppo annunci, incluse offerte CPC e target.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_change_history`
Cronologia modifiche delle entita account con le modifiche recenti.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `resource_type` | No | Filtro per tipo risorsa |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

### Gerarchia Account e Merchant Center

#### `gads_list_customer_clients`
Lista account cliente sotto un account manager (MCC).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID account manager |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_accessible_customers`
Lista tutti gli account cliente accessibili con le credenziali correnti.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `response_format` | No | `markdown` o `json` |

---

#### `gads_list_merchant_center_links`
Lista account Merchant Center collegati all'account Google Ads.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

**Campi restituiti:** ID Merchant, Nome Account, Stato

---

### Viste Performance

#### `gads_geographic_view`
Dati performance basati sulla localita dalla vista geografica.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_shopping_performance_view`
Dati performance Shopping a livello prodotto.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_display_keyword_view`
Dati performance keyword display.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_topic_view`
Dati performance targeting per argomento.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_user_location_view`
Dati performance per posizione fisica dell'utente.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_click_view`
Dati a livello click con GCLID, localita e info dispositivo.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | No | Filtro per ID campagna |
| `start_date` | No | Data inizio YYYY-MM-DD (default: 30 giorni fa) |
| `end_date` | No | Data fine YYYY-MM-DD (default: oggi) |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

### Keyword Planner e GAQL

#### `gads_generate_keyword_ideas`
Generazione suggerimenti keyword tramite Google Ads Keyword Planner.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `keywords` | Si | Keyword seed (separate da virgola o lista) |
| `language_id` | No | ID criterio lingua (default: inglese) |
| `geo_target_id` | No | ID criterio target geografico |
| `limit` | No | Risultati max (default: 50) |
| `offset` | No | Offset paginazione |
| `response_format` | No | `markdown` o `json` |

---

#### `gads_execute_gaql`
Esecuzione query personalizzate in Google Ads Query Language (GAQL).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `query` | Si | Query GAQL completa |
| `limit` | No | Risultati max |
| `response_format` | No | `markdown` o `json` |

---

## Tool di Scrittura (26)

### Gestione Campagne

#### `gads_create_campaign`
Creazione nuova campagna con budget e strategia di offerta.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `name` | Si | Nome campagna |
| `campaign_type` | Si | `SEARCH`, `DISPLAY`, `SHOPPING`, `VIDEO`, `PERFORMANCE_MAX`, `DEMAND_GEN` |
| `bidding_strategy_type` | Si | `MANUAL_CPC`, `TARGET_CPA`, `TARGET_ROAS`, `MAXIMIZE_CONVERSIONS`, `MAXIMIZE_CONVERSION_VALUE`, `MAXIMIZE_CLICKS` |
| `budget_amount_micros` | Si | Budget giornaliero in micros (es. `10000000` = $10) |
| `start_date` | No | Data inizio YYYY-MM-DD |
| `end_date` | No | Data fine YYYY-MM-DD |
| `target_cpa_micros` | No | CPA target in micros (per TARGET_CPA) |
| `target_roas` | No | ROAS target (per TARGET_ROAS) |

---

#### `gads_update_campaign`
Aggiornamento impostazioni campagna (nome, date inizio/fine).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna da aggiornare |
| `name` | No | Nuovo nome campagna |
| `start_date` | No | Nuova data inizio YYYY-MM-DD |
| `end_date` | No | Nuova data fine YYYY-MM-DD |

---

#### `gads_set_campaign_status`
Modifica stato campagna (attiva, pausa o rimozione).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `status` | Si | `enable`, `pause` o `remove` |

---

#### `gads_update_budget`
Aggiornamento budget giornaliero campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `budget_id` | Si | ID risorsa budget |
| `amount_micros` | Si | Nuovo budget giornaliero in micros |

---

#### `gads_set_bidding_strategy`
Impostazione o modifica strategia di offerta campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `strategy_type` | Si | `MANUAL_CPC`, `TARGET_CPA`, `TARGET_ROAS`, `MAXIMIZE_CONVERSIONS`, `MAXIMIZE_CONVERSION_VALUE`, `MAXIMIZE_CLICKS` |
| `target_cpa_micros` | No | CPA target in micros |
| `target_roas` | No | ROAS target |

---

### Gestione Gruppi Annunci e Annunci

#### `gads_create_ad_group`
Creazione nuovo gruppo annunci in una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna padre |
| `name` | Si | Nome gruppo annunci |
| `ad_group_type` | Si | `SEARCH_STANDARD`, `DISPLAY_STANDARD`, `SHOPPING_PRODUCT`, `VIDEO_RESPONSIVE` |
| `cpc_bid_micros` | No | Offerta CPC predefinita in micros |

---

#### `gads_set_ad_group_status`
Modifica stato gruppo annunci (attiva, pausa o rimozione).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci |
| `status` | Si | `enable`, `pause` o `remove` |

---

#### `gads_set_ad_status`
Modifica stato annuncio (attiva, pausa o rimozione).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci contenente l'annuncio |
| `ad_id` | Si | ID annuncio |
| `status` | Si | `enable`, `pause` o `remove` |

---

#### `gads_create_responsive_search_ad`
Creazione Annuncio Adattabile della Rete di Ricerca (RSA) in un gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci target |
| `headlines` | No | Lista titoli (3-15, max 30 caratteri ciascuno) |
| `descriptions` | No | Lista descrizioni (2-4, max 90 caratteri ciascuna) |
| `final_urls` | No | URL pagina di destinazione |
| `path1` | No | Percorso URL visualizzato 1 (max 15 caratteri) |
| `path2` | No | Percorso URL visualizzato 2 (max 15 caratteri) |

---

#### `gads_create_ad_extension`
Creazione estensione annuncio (sitelink, callout, chiamata o snippet strutturato).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | Campagna a cui collegare l'estensione |
| `extension_type` | Si | `SITELINK`, `CALLOUT`, `CALL`, `STRUCTURED_SNIPPET` |
| `link_text` | No | Testo sitelink |
| `final_urls` | No | URL sitelink |
| `description1` | No | Descrizione sitelink riga 1 |
| `description2` | No | Descrizione sitelink riga 2 |
| `callout_text` | No | Testo callout |
| `phone_number` | No | Numero telefono estensione chiamata |
| `country_code` | No | Prefisso internazionale telefono |
| `snippet_header` | No | Intestazione snippet strutturato |
| `snippet_values` | No | Valori snippet strutturato |

---

### Keyword

#### `gads_add_keywords`
Aggiunta keyword positive a un gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci target |
| `keywords` | No | Lista stringhe keyword |
| `match_type` | No | `exact`, `phrase` o `broad` |
| `cpc_bid_micros` | No | Offerta CPC in micros |

---

#### `gads_update_keyword`
Aggiornamento offerta o stato di una keyword.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci |
| `criterion_id` | Si | ID criterio keyword |
| `cpc_bid_micros` | No | Nuova offerta CPC in micros |
| `status` | No | `enable`, `pause` o `remove` |

---

#### `gads_add_negative_keywords`
Aggiunta keyword negative a campagna o gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `level` | Si | `campaign` o `ad_group` |
| `campaign_id` | No | ID campagna (obbligatorio se level=campaign) |
| `ad_group_id` | No | ID gruppo annunci (obbligatorio se level=ad_group) |
| `keywords` | No | Lista stringhe keyword negative |
| `match_type` | No | `exact`, `phrase` o `broad` |

---

### Creazione Annunci (Avanzata)

#### `gads_create_responsive_display_ad`
Creazione Annuncio Display Responsive in un gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci target |
| `marketing_image_asset_ids` | No | ID asset immagini marketing |
| `headlines` | No | Titoli brevi (max 30 caratteri) |
| `long_headline` | No | Titolo lungo (max 90 caratteri) |
| `descriptions` | No | Descrizioni (max 90 caratteri) |
| `business_name` | No | Nome attivita (max 25 caratteri) |
| `final_urls` | No | URL pagina di destinazione |
| `logo_asset_ids` | No | ID asset logo |
| `square_image_asset_ids` | No | ID asset immagini quadrate |

---

#### `gads_create_demand_gen_ad`
Creazione annuncio Demand Gen multi-asset.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci target |
| `headlines` | No | Titoli |
| `descriptions` | No | Descrizioni |
| `marketing_image_asset_ids` | No | ID asset immagini marketing |
| `logo_asset_id` | No | ID asset logo |
| `business_name` | No | Nome attivita |
| `final_urls` | No | URL pagina di destinazione |
| `call_to_action` | No | Tipo CTA |

---

#### `gads_create_video_ad`
Creazione annuncio video in un gruppo annunci.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `ad_group_id` | Si | ID gruppo annunci target |
| `video_asset_id` | Si | ID asset video YouTube |
| `ad_format` | Si | `IN_STREAM_SKIPPABLE`, `IN_STREAM_NON_SKIPPABLE`, `BUMPER`, `VIDEO_RESPONSIVE` |
| `headline` | No | Titolo annuncio |
| `description` | No | Descrizione annuncio |
| `final_url` | No | URL pagina di destinazione |
| `display_url` | No | URL visualizzato |
| `companion_banner_asset_id` | No | ID asset banner companion |

---

### Targeting

#### `gads_set_location_targeting`
Impostazione targeting geografico per una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `location_ids` | No | ID costanti target geografici Google |
| `exclude` | No | Escludi localita invece di targetizzarle |

---

#### `gads_set_language_targeting`
Impostazione targeting per lingua per una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `language_ids` | No | ID criteri lingua |

---

#### `gads_set_device_targeting`
Impostazione modificatore offerta per dispositivo per una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `device` | Si | `MOBILE`, `DESKTOP` o `TABLET` |
| `bid_modifier` | Si | Modificatore offerta (es. `1.2` = +20%, `0` = escludi) |

---

#### `gads_set_demographic_targeting`
Impostazione targeting demografico per una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `dimension` | Si | `AGE`, `GENDER`, `PARENTAL_STATUS` o `INCOME` |
| `values` | No | Valori target per la dimensione |
| `bid_modifier` | No | Modificatore offerta |

---

#### `gads_create_audience_segment`
Aggiunta segmento di pubblico a una campagna.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `audience_type` | Si | `IN_MARKET`, `AFFINITY`, `CUSTOM_INTENT`, `REMARKETING` |
| `audience_id` | Si | ID segmento di pubblico |
| `bid_modifier` | No | Modificatore offerta |

---

### Asset e Shopping

#### `gads_create_asset`
Creazione asset riutilizzabile (testo, immagine, video o CTA).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `asset_type` | Si | `TEXT`, `IMAGE`, `YOUTUBE_VIDEO`, `MEDIA_BUNDLE`, `CALL_TO_ACTION` |
| `name` | Si | Nome asset |
| `text_content` | No | Contenuto testo (per tipo TEXT) |
| `image_url` | No | URL immagine (per tipo IMAGE) |
| `youtube_video_id` | No | ID video YouTube (per tipo YOUTUBE_VIDEO) |
| `call_to_action_type` | No | Tipo CTA (per tipo CALL_TO_ACTION) |

---

#### `gads_create_asset_group`
Creazione gruppo di asset per campagna Performance Max o Demand Gen.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna PMax/DG |
| `name` | Si | Nome gruppo di asset |
| `final_urls` | No | URL pagina di destinazione |
| `final_mobile_urls` | No | URL pagina di destinazione mobile |
| `path1` | No | Percorso URL visualizzato 1 |
| `path2` | No | Percorso URL visualizzato 2 |

---

#### `gads_add_asset_group_assets`
Collegamento asset a un gruppo di asset (per campagne PMax/DG).

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `asset_group_id` | Si | ID gruppo di asset |
| `asset_ids` | No | ID asset da collegare |
| `field_types` | No | Tipi campo asset (`HEADLINE`, `DESCRIPTION`, `MARKETING_IMAGE`, `LOGO`, ecc.) |

---

#### `gads_set_listing_group_filter`
Impostazione filtro gruppo schede per gruppo asset PMax o Shopping.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `asset_group_id` | Si | ID gruppo di asset |
| `filter_type` | Si | Tipo filtro |
| `dimension` | Si | `BRAND`, `CATEGORY_L1`, `CATEGORY_L2`, `PRODUCT_TYPE_L1`, `PRODUCT_TYPE_L2`, `CUSTOM_LABEL_0`, `CUSTOM_LABEL_1`, `ITEM_ID`, `CONDITION` |
| `value` | No | Valore dimensione |
| `parent_filter_id` | No | ID filtro padre per suddivisione |

---

#### `gads_link_merchant_center`
Collegamento account Merchant Center a campagna Shopping o PMax.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `campaign_id` | Si | ID campagna |
| `merchant_id` | Si | ID account Merchant Center |
| `feed_label` | No | Etichetta feed |
| `sales_country` | No | Codice paese vendita |

---

### Conversioni e Liste Clienti

#### `gads_upload_click_conversions`
Upload conversione click offline su Google Ads.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `conversion_action_id` | Si | ID risorsa azione di conversione |
| `gclid` | Si | Google Click ID |
| `conversion_date_time` | Si | Data/ora conversione (YYYY-MM-DD HH:MM:SS+HH:MM) |
| `conversion_value` | No | Valore conversione |
| `currency_code` | No | Codice valuta (es. `USD`, `EUR`) |

---

#### `gads_upload_customer_list`
Upload membri in una lista customer match.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `user_list_id` | Si | ID risorsa lista utenti |
| `emails` | No | Lista indirizzi email (hash SHA256) |
| `phones` | No | Lista numeri telefono (hash SHA256) |

---

#### `gads_remove_customer_list_members`
Rimozione membri da una lista customer match.

| Parametro | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `customer_id` | Si | ID cliente Google Ads |
| `user_list_id` | Si | ID risorsa lista utenti |
| `emails` | No | Indirizzi email da rimuovere |
| `phones` | No | Numeri telefono da rimuovere |

---

## Parametri Comuni

Tutti i tool di lettura condividono questi parametri comuni:

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `customer_id` | — | Obbligatorio. Accetta formato `1234567890` o `123-456-7890` |
| `limit` | 50 | Risultati per pagina (1-1000) |
| `offset` | 0 | Offset paginazione |
| `response_format` | `markdown` | `markdown` per tabelle leggibili, `json` per dati strutturati |

I tool con intervallo date usano gli **ultimi 30 giorni** come default quando `start_date` e `end_date` non vengono specificati.

## Valori Monetari

Tutti i valori monetari usano i **micros** (1 unita = 1.000.000 micros):

| Importo | Valore Micros |
|---------|--------------|
| $1,00 | `1000000` |
| $10,00 | `10000000` |
| $50,00 | `50000000` |
| $100,00 | `100000000` |
