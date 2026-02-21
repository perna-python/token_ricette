# token_ricette
Programma per visualizzare il token per le ricette bianche da inserire nel gestionale della farmacia e la visualizzazione del token per la procedura di emergenza quando non funzionano le ricette elettroniche

# Installazione

## Requisiti generali

Il programma è scritto in Python e richiede un'installazione di Python 3.11 (o superiore) presente nel sistema. Inoltre usa il package manager `pip` per installare le dipendenze elencate in `requirements.txt`.

Per installare i requisiti di base:

```bash
pip install -r requirements.txt
```

### Linux

Su Linux è richiesto anche un piccolo pacchetto aggiuntivo per la gestione degli appunti (`clipboard`) perché il programma copia automaticamente il token. Installare `xclip` con il comando:

```bash
sudo apt-get install xclip    # distribuzioni debian/ubuntu
# oppure usare il package manager della propria distribuzione
``` 

Una volta installato `xclip` eseguire la procedura generale sopra per le dipendenze Python.

### Windows e macOS

Non sono richieste dipendenze extra al di fuori di quelle in `requirements.txt`. Dopo aver installato Python + pip, si possono seguire i comandi generali:

```powershell
pip install -r requirements.txt
```

> ⚠️ Su macOS potrebbe essere necessario usare `pip3` a seconda della configurazione del sistema.

## Avvio

Dopo l'installazione aprire un terminale (o PowerShell su Windows) nella cartella del progetto e lanciare:

```bash
python main.py
```

Questo avvierà l'interfaccia grafica basata su [Flet](https://flet.dev/); il 
programma mostra i token ricevuti per email se ancora validi. Per richiedere
un nuovo token per le ricette elettroniche richiederlo direttamente dal
gestionale che si utilizza in farmacia invece per il sito di continuità
per le ricette elettroniche si può richiedere direttamente premendo sul
pulsante richiedi nuovo token.

## Configurazione

Il file `token_ricette/config_example.py` contiene un esempio di configurazione. Copiare il contenuto in `config.py` e impostare i parametri necessari come descritto nel modulo stesso.

## Supporto e contributi

Per segnalare bug o proporre miglioramenti, aprire un issue su GitHub nel repository [perna-python/token_ricette](https://github.com/perna-python/token_ricette).

---

