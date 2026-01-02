# 🚀 Opzioni Hosting per AllFoodSicily

## Requisiti del Progetto

- **Bot Telegram interattivo** (polling o webhook)
- **Processo long-running** (bot sempre attivo)
- **Scheduler giornaliero** (workflow alle 9:00)
- **Job lunghi** (2-5 minuti per workflow)
- **Generazione PDF** (storage temporaneo)
- **Python 3.10+**
- **Nessun database** (solo file temporanei)

---

## 🏆 Opzioni Consigliate (Top 3)

### 1. **Railway** ⭐ CONSIGLIATO

**Perché scegliere Railway:**
- ✅ Setup semplicissimo (deploy da GitHub in 2 click)
- ✅ Supporto nativo per processi long-running
- ✅ Free tier generoso ($5 crediti/mese)
- ✅ Auto-deploy da Git
- ✅ Logs in tempo reale
- ✅ Environment variables facili
- ✅ Supporto Python perfetto

**Pricing:**
- **Free**: $5 crediti/mese (sufficiente per bot piccolo)
- **Pro**: $5/mese + usage (circa $10-15/mese totale)

**Setup:**
```bash
# 1. Push su GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo>
git push -u origin main

# 2. Su Railway:
# - New Project → Deploy from GitHub
# - Seleziona repo
# - Railway auto-rileva Python
# - Aggiungi variabili .env
# - Deploy!
```

**File necessario:** `Procfile` o `railway.json`
```procfile
web: python main.py
```

**Vantaggi:**
- Zero configurazione
- Scaling automatico
- HTTPS incluso
- Database opzionale (se serve in futuro)

**Svantaggi:**
- Free tier limitato
- Meno controllo rispetto a VPS

---

### 2. **Render** 🥈

**Perché scegliere Render:**
- ✅ Free tier disponibile (con limiti)
- ✅ Setup semplice
- ✅ Auto-deploy da Git
- ✅ Supporto Python

**Pricing:**
- **Free**: Processo si spegne dopo 15 min di inattività (❌ non adatto per bot sempre attivo)
- **Starter**: $7/mese (processo sempre attivo)

**Setup:**
```bash
# Simile a Railway, ma richiede configurazione webhook
# per evitare che il processo si spenga
```

**Svantaggi:**
- Free tier non adatto (processo si spegne)
- Meno flessibile di Railway

---

### 3. **Fly.io** 🥉

**Perché scegliere Fly.io:**
- ✅ Ottimo per long-running processes
- ✅ Free tier generoso (3 VM gratuite)
- ✅ Globale (edge locations)
- ✅ Pricing chiaro

**Pricing:**
- **Free**: 3 VM shared-cpu-1x (256MB RAM)
- **Paid**: $1.94/mese per VM sempre attiva

**Setup:**
```bash
# Installa flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Inizializza progetto
fly launch

# Deploy
fly deploy
```

**File necessario:** `fly.toml`
```toml
app = "allfoodsicily"
primary_region = "fra"  # Frankfurt (vicino all'Italia)

[build]

[env]
  PYTHONUNBUFFERED = "1"

[[services]]
  internal_port = 8080
  protocol = "tcp"
```

**Vantaggi:**
- Molto economico
- Globale
- Ottimo per bot

**Svantaggi:**
- Setup leggermente più complesso
- CLI necessario

---

## 💰 Opzioni Economiche (VPS)

### 4. **Hetzner Cloud** 💸 MIGLIORE RAPPORTO QUALITÀ/PREZZO

**Perché scegliere Hetzner:**
- ✅ **€4.15/mese** per VPS (CX11)
- ✅ 2GB RAM, 20GB SSD
- ✅ Performance eccellente
- ✅ Data center in Germania (bassa latenza)
- ✅ Controllo totale

**Pricing:**
- **CX11**: €4.15/mese (2GB RAM, 1 vCPU)
- **CX21**: €5.83/mese (4GB RAM, 2 vCPU) - consigliato

**Setup:**
```bash
# 1. Crea VPS su Hetzner
# 2. SSH nel server
ssh root@your-server-ip

# 3. Installa Python e dipendenze
apt update && apt install -y python3.10 python3-pip python3-venv git

# 4. Clona e setup progetto
git clone <your-repo>
cd allfoodsicily
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Setup systemd service
sudo nano /etc/systemd/system/allfoodsicily.service
```

**File systemd service:**
```ini
[Unit]
Description=AllFoodSicily Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/allfoodsicily
Environment="PATH=/path/to/allfoodsicily/venv/bin"
ExecStart=/path/to/allfoodsicily/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Gestione:**
```bash
# Avvia
sudo systemctl start allfoodsicily

# Abilita all'avvio
sudo systemctl enable allfoodsicily

# Status
sudo systemctl status allfoodsicily

# Logs
sudo journalctl -u allfoodsicily -f
```

**Vantaggi:**
- Prezzo imbattibile
- Controllo totale
- Performance ottime
- Storage illimitato (quasi)

**Svantaggi:**
- Richiede conoscenze Linux
- Manutenzione manuale
- Nessun auto-scaling

---

### 5. **Contabo** 💸

**Pricing:**
- **VPS S**: €4.99/mese (4GB RAM, 2 vCPU)
- Performance buone, prezzo competitivo

Simile a Hetzner, ma con più storage incluso.

---

## 🏢 Opzioni Enterprise

### 6. **DigitalOcean App Platform**

**Pricing:**
- **Basic**: $5/mese + usage
- Professionale, ma più costoso

**Vantaggi:**
- Molto affidabile
- Supporto eccellente
- Integrazione con altri servizi DO

---

### 7. **AWS / GCP / Azure**

**Quando usarli:**
- Se hai già account enterprise
- Se serve integrazione con altri servizi cloud
- Se hai budget elevato

**Pricing:**
- Complesso (pay-per-use)
- Può essere costoso se non ottimizzato

**Servizi utili:**
- **AWS**: EC2, Lambda (per job), ECS
- **GCP**: Cloud Run, Compute Engine
- **Azure**: App Service, Container Instances

---

## 🎯 Raccomandazione Finale

### Per iniziare rapidamente:
**Railway** - Setup in 5 minuti, funziona subito

### Per risparmiare:
**Hetzner Cloud** - €4.15/mese, performance ottime

### Per massima flessibilità:
**Fly.io** - Free tier generoso, globale

---

## 📋 Checklist Pre-Deploy

### 1. Preparare il progetto
```bash
# Assicurati che funzioni localmente
python main.py --validate

# Test completo
python main.py --now
```

### 2. File necessari per deploy

**`.dockerfile` (opzionale, per container):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**`.dockerignore`:**
```
venv/
__pycache__/
*.pyc
.env
logs/
*.log
.git/
```

**`Procfile` (per Railway/Render):**
```
web: python main.py
```

### 3. Environment Variables

Assicurati di avere tutte le variabili nel pannello hosting:
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TIMEZONE=Europe/Rome`
- `DEBUG_MODE=false`

### 4. Telegram Webhook vs Polling

**Polling (attuale):**
- ✅ Funziona ovunque
- ✅ Nessuna configurazione
- ❌ Consuma risorse (controlla continuamente)

**Webhook (consigliato per produzione):**
- ✅ Più efficiente
- ✅ Risposta immediata
- ❌ Richiede URL pubblico HTTPS

**Per abilitare webhook:**
```python
# In main.py, invece di start_polling():
await app.updater.start_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", "8080")),
    url_path=settings.TELEGRAM_BOT_TOKEN,
    webhook_url=f"https://your-domain.com/{settings.TELEGRAM_BOT_TOKEN}"
)
```

---

## 🔧 Configurazione Consigliata

### Railway (Setup Completo)

1. **Crea account Railway**
2. **New Project → Deploy from GitHub**
3. **Aggiungi variabili .env** nel pannello
4. **Deploy automatico!**

### Hetzner (Setup Completo)

1. **Crea VPS CX21** (€5.83/mese)
2. **SSH e setup base:**
```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install -y python3.10 python3-pip python3-venv git nginx

# Clone repo
cd /opt
git clone <your-repo> allfoodsicily
cd allfoodsicily

# Setup venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env  # Aggiungi tutte le variabili

# Setup systemd
sudo nano /etc/systemd/system/allfoodsicily.service
# (vedi esempio sopra)

# Start service
sudo systemctl start allfoodsicily
sudo systemctl enable allfoodsicily
```

3. **Monitoraggio:**
```bash
# Logs in tempo reale
sudo journalctl -u allfoodsicily -f

# Restart se necessario
sudo systemctl restart allfoodsicily
```

---

## 💡 Tips & Tricks

### 1. Keep-Alive per Render Free Tier
Se usi Render free tier, aggiungi un ping ogni 10 minuti:
```python
# In main.py
import requests

async def keep_alive():
    while True:
        await asyncio.sleep(600)  # 10 minuti
        requests.get("https://your-app.onrender.com/health")
```

### 2. Health Check Endpoint
Aggiungi endpoint per health check:
```python
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

### 3. Log Rotation
Su VPS, configura log rotation:
```bash
sudo nano /etc/logrotate.d/allfoodsicily
```

```
/path/to/allfoodsicily/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### 4. Backup
Su VPS, backup automatico:
```bash
# Crea script backup
nano /usr/local/bin/backup-allfoodsicily.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backup/allfoodsicily-$DATE.tar.gz /opt/allfoodsicily
find /backup -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Crontab (backup giornaliero)
0 2 * * * /usr/local/bin/backup-allfoodsicily.sh
```

---

## 📊 Confronto Rapido

| Servizio | Prezzo | Setup | Manutenzione | Consigliato per |
|----------|--------|-------|--------------|-----------------|
| **Railway** | $5-15/mese | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Iniziare |
| **Hetzner** | €4-6/mese | ⭐⭐⭐ | ⭐⭐⭐ | Budget limitato |
| **Fly.io** | $0-2/mese | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free tier |
| **Render** | $7/mese | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Alternativa Railway |
| **DigitalOcean** | $5+/mese | ⭐⭐⭐ | ⭐⭐⭐⭐ | Professionale |

---

## 🚀 Quick Start: Railway (5 minuti)

```bash
# 1. Push su GitHub
git init
git add .
git commit -m "Ready for deploy"
git remote add origin <your-repo-url>
git push -u origin main

# 2. Su Railway.app:
# - Login con GitHub
# - New Project → Deploy from GitHub
# - Seleziona repo
# - Add Environment Variables (copia da .env)
# - Deploy!

# 3. Bot attivo! 🎉
```

---

## ❓ Domande Frequenti

**Q: Quale servizio è più economico?**
A: Hetzner Cloud (€4.15/mese) o Fly.io free tier

**Q: Quale è più semplice da setup?**
A: Railway (deploy in 2 click)

**Q: Il bot funziona 24/7?**
A: Sì, su tutti i servizi pagati. Render free tier si spegne dopo inattività.

**Q: Posso cambiare servizio dopo?**
A: Sì, il codice è portabile. Basta cambiare variabili d'ambiente.

**Q: Serve un database?**
A: No, il progetto non usa database. Solo file temporanei e Google Docs.

**Q: Quanto costa mensilmente?**
A: Dipende dal servizio:
- Railway: ~$10-15/mese
- Hetzner: €4-6/mese
- Fly.io: $0-2/mese (free tier generoso)

---

## 📞 Supporto

Per problemi di deploy, consulta:
- Documentazione Railway: https://docs.railway.app
- Documentazione Hetzner: https://docs.hetzner.com
- Documentazione Fly.io: https://fly.io/docs

