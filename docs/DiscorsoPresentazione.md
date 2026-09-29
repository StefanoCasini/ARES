# ARES - Presentazione

### Slide 1: Titolo e Introduzione

* **Visivo:** Logo A.R.E.S. e dati del progetto.


* **Discorso:**

> "Buongiorno a tutti. Oggi presento A.R.E.S., acronimo di *Automated Reconnaissance & Enumeration System*, un framework sviluppato nell'ambito dell'attività progettuale di Sicurezza dell'Informazione in collaborazione con Cryptonet Labs.
> L'obiettivo del progetto è stato automatizzare, standardizzare e ottimizzare la fase iniziale di un Network Penetration Test: la *Reconnaissance*."
> 
> 

---

### Slide 2: Limiti Approccio Manuale & Obiettivi del Progetto

* **Visivo:** Colonne con eterogeneità/incoerenza/chaos artifact e gli obiettivi tecnici del framework.


* **Discorso:**

> "Nelle attività operative di ricognizione di rete ci si scontra subito con i limiti dell'approccio manuale:
> 
> 
> 1. **Eterogeneità dei formati**: ogni tool genera output proprietari non interoperabili (XML per Nmap, JSON grezzi per Masscan o formati grepable).
> 
> 
> 2. **Incoerenza strutturale**: tool volumetrici restituiscono flussi a eventi non ordinati, mentre scanner di servizio aggregano per host, rendendo complessa la correlazione delle evidenze su uno stesso target.
> 
> 
> 3. **Gestione caotica degli artifact**: lanciare molteplici comandi disperde file grezzi nel filesystem senza un tracciamento chiaro di target e timestamp.
> 
> 
> 
> 
> A.R.E.S. risponde a queste criticità integrando in una sola pipeline l'orchestrazione ibrida di scanner attivi e passivi, la normalizzazione tramite DTO tipizzati, un'interfaccia dichiarativa YAML e la generazione di un unico report JSON interoperabile e pronto per downstream pipeline di security."
> 
> 

---

### Slide 3: Active vs Passive – Il Trade-off della Visibilità

* **Visivo:** Confronto tra scansione attiva e passiva nel contesto delle RoE.


* **Discorso:**

> "La ricognizione non è mai puramente tecnica, ma è subordinata alle *Rules of Engagement* (RoE) concordate con il cliente. Questo impone la gestione di un trade-off fondamentale tra profondità informativa e rilevabilità:
> 
> 
> * **Active Reconnaissance**: basata su tool come Nmap e Masscan. Richiede interazione diretta a livello di pacchetto di rete, garantendo massima accuratezza e service versioning aggiornato, ma con alto 'rumore' e rischio di rilevamento da parte di IDS/IPS.
> 
> 
> * **Passive Reconnaissance**: integrata via Smap sfruttando le API e i dati storici di Shodan. Approccio zero-touch, totalmente invisibile ai sensori perimetrali del perimetro target perché interroga record già indicizzati.
> A.R.E.S. è progettato per bilanciare o combinare queste due anime in base ai vincoli contrattuali dello scenario."
> 
> 
> 
> 

---

### Slide 4: Architettura del Sistema

* **Visivo:** Pipeline `CONFIG -> LAUNCH -> PARSING -> MERGE -> REPORT`.


* **Discorso:**

> "L'architettura del software è organizzata come una pipeline sequenziale a cinque stadi:
> 
> 
> 1. **Config**: parsing del file YAML e generazione dei task da eseguire.
> 
> 
> 2. **Launch**: orchestrazione concorrente multi-thread dei comandi shell associati ai tool. In questa fase il launcher effettua anche un 'wrapping' per tracciare il comando generatore sui file raw.
> 
> 
> 3. **Parsing**: dispatching dinamico e normalizzazione dei file grezzi (inclusi eventuali log storici iniettati dall'utente).
> 
> 
> 4. **Merge**: data fusion agnostica e accumulo delle evidenze.
> 
> 
> 5. **Report**: esportazione del payload finale consolidato in formato JSON standardizzato."
> 
> 
> 
> 

---

### Slide 5: Pattern & Estensibilità

* **Visivo:** Strategy Pattern e Data Transfer Objects (DTO).


* **Discorso:**

> "A livello implementativo, la priorità è stata garantire la totale manutenibilità ed estendibilità:
> 
> 
> * **Strategy Pattern**: implementato tramite le interfacce astratte `CommandGenerator` (per tradurre i parametri YAML in comandi shell) e `BaseParser` (con il metodo `can_handle` per il riconoscimento automatico del formato e `parse` per l'estrazione). Aggiungere un nuovo tool significa solo implementare queste due classi, lasciando intatto il core.
> 
> 
> * **Data Transfer Objects (DTO)**: il passaggio dati interno non usa dizionari generici, ma strutture tipizzate (`HostDTO`, `PortDTO`, `OSDTO`). Questo funge da contratto rigido tra parser e motore di fusione.
> 
> 
> * **Requisito di sistema**: il tool richiede privilegi di root e Linux nativo, poiché sia le scansioni SYN stealth di Nmap sia l'iniezione asincrona ad alta velocità di Masscan richiedono l'apertura e l'interazione con socket raw a basso livello, bypassando lo stack TCP/IP del kernel."
> 
> 
> 
> 

---

### Slide 6: Modulo Merger & Data Fusion

* **Visivo:** Tabella con IP, porte, fonti diverse e stato finale aggregato.


* **Discorso:**

> "Il modulo Merger è il collettore logico del framework. La sua caratteristica chiave è che non applica una logica di semplice sovrascrittura, ma un principio di **Accumulo e Consolidamento delle Evidenze**:
> Come mostra la tabella: se su un host la porta 80 viene vista sia da Nmap che da Masscan, A.R.E.S. correla entrambe le fonti: conserva la certezza dello stato aperta di Nmap e aggrega il banner catturato da Masscan, ottenendo il record più completo possibile senza ripetere scansioni costose.
> Parallelamente, se un servizio viene visto solo in discovery rapida o solo su una sorgente, l'informazione viene preservata con l'indicazione precisa del tool sorgente."
> 
> 

---

### Slide 7: Configurazione YAML

* **Visivo:** Estratto del file `config.yml`.


* **Discorso:**

> "Nessuna logica operativa è codificata 'hard-coded' nel sorgente Python. L'intero comportamento del sistema è governato dal file `config.yml`:
> L'operatore può:
> 
> 
> * Definire il livello di concorrenza con `n_threads`;
> 
> 
> * Abilitare o disabilitare specifici moduli o singoli task atomici (come un ping sweep rispetto a una top 100 TCP ports);
> 
> 
> * Regolare parametri verticali, come il `rate` limit per Masscan per rispettare i limiti di banda concordati nelle RoE;
> 
> 
> * E persino importare file raw di scansioni pregresse tramite la direttiva `import_files`, per includere dati offline nella fase di fusione senza toccare la rete."
> 
> 
> 
> 

---

### Slide 8: Analisi del Report Finale

* **Visivo:** Preview del JSON risultante con campi `commands`, `ports`, `hostnames`, `os`.


* **Discorso:**

> "Questo è l'output finale: un file JSON strutturato deterministico.
> Notiamo tre aspetti determinanti:
> 
> 
> 1. **Tracciabilità e Audit trail**: nella radice e all'interno dell'host è memorizzato l'elenco esatto dei comandi CLI eseguiti, elemento fondamentale per compliance e verifiche legali post-test.
> 
> 
> 2. **Multi-Source Evidence**: per la porta 80 sono presenti i blocchi di Nmap e Masscan con il relativo TTL e banner HTTP. Per la porta 443 vediamo la presenza del dato derivato da Smap (API Shodan), utile per confrontare lo stato attuale con quello storico.
> 
> 
> 3. **Machine Readable**: la struttura gerarchica per host, porte, OS e CPE è immediatamente pronta per essere inviata a SIEM o a motori di vulnerability scanning."
> 
> 
> 
> 

---

### Slide 9: Sviluppi Futuri e Conclusioni

* **Visivo:** Web GUI, Integrazione Nuclei, Containerizzazione.


* **Discorso:**

> "Per quanto riguarda l'evoluzione della piattaforma, i prossimi step prevedono:
> 
> 
> * Lo sviluppo di una **Web GUI** per la gestione visuale della configurazione e la navigazione a grafo dei report aggregati;
> 
> 
> * L'integrazione di **Nuclei**, per estendere A.R.E.S. dalla sola enumerazione di rete al Vulnerability Assessment automatico basato su template;
> 
> 
> * La **containerizzazione** tramite Docker ottimizzato per standardizzare l'ambiente di rete ed estendere la portabilità del tool.
> 
> 
> 
> 
> In sintesi, A.R.E.S. dimostra come l'orchestrazione e la normalizzazione automatizzata possano eliminare i colli di bottiglia manuali della reconnaissance, fornendo dati coerenti e pronti per le fasi operative successive di un penetration test.
> Vi ringrazio per l'attenzione."
> 
> 

---

### Consigli per la presentazione:

1. **Puntare sul disaccoppiamento:** Quando parli della Slide 5, rimarca che il Merger *non sa* cosa sia Nmap o Masscan; elabora solo oggetti `PortDTO`/`HostDTO`. Questo è il valore ingegneristico principale.


2. **Tempo sulla Slide 8:** È la slide più densa. Non leggere il JSON riga per riga; evidenzia solo come un blocco arrivi dalla scansione attiva e uno da Shodan/Smap.
