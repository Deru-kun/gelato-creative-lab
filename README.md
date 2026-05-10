# Gelato Creative Lab 🍦🔬

Un sistema avanzato di ETL e Dashboard Conversazionale per la gestione e l'ideazione di gusti gelato basato su cataloghi industriali (Leagel, Proni, Rubicone).

## 🚀 Funzionalità
- **ETL Pipeline**: Parsing automatico di cataloghi Markdown/PDF in dati strutturati.
- **Unified Database**: Oltre 1.100 ingredienti tecnici mappati su Supabase.
- **Conversational Dashboard**: Interfaccia stile Gemini per ideare gusti partendo da concept creativi.
- **Smart Matching**: Algoritmo di ricerca per trovare le migliori Paste, Variegature e Inclusioni.

## 🛠️ Tech Stack
- **Backend**: Python (Parsing & Classification), Node.js (API Server).
- **Database**: PostgreSQL (Supabase).
- **Frontend**: Vanilla JS, CSS Glassmorphism, React-ready structure.

## 📦 Installazione
1. Clona il repository.
2. Installa le dipendenze Python: `pip install -r requirements.txt`.
3. Installa le dipendenze Node: `cd frontend && npm install`.
4. Configura il file `.env` con la tua `DB_URL` di Supabase.

## 🖥️ Utilizzo
1. Avvia il server: `cd frontend && node server.js`.
2. Apri `http://localhost:3001` nel browser.
