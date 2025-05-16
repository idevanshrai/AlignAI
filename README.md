# AlignAI 🧠📄

**AlignAI** is an AI-powered resume analyzer that compares your resume with any job description to highlight skill matches, calculate similarity scores, and suggest improvements — all in a sleek, minimal web interface.

---

## 🔧 Features

- 📄 **Resume Upload** – Upload your resume in PDF format.  
- 📌 **Job Description Input** – Paste any JD to compare against.  
- 🧠 **Smart Scoring System** – Combines TF-IDF, BERT Embeddings & Skill Match.  
- 🎯 **Skill Insights** – Shows matched and missing skills instantly.  
- 🌑 **Dark Mode UI** – With a custom splash screen and animated visuals.  
- 📊 **Final Score Breakdown** – Transparent metrics for better clarity.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)  
- **Backend**: Python (Flask)  
- **AI/NLP**: SentenceTransformers, Scikit-learn, NLTK  
- **Parsing**: PyMuPDF (PDF), Custom skill extractor

---

## 🚀 Getting Started (Local Setup)

### 1. Clone the Repository

```bash
git clone https://github.com/idevanshrai/AlignAI.git
cd AlignAI
````

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Flask Server

```bash
python app.py
```

### 4. Open Frontend in Browser

Open `frontend/splash.html` or `frontend/index.html` to use the app.

---

## 📁 Project Structure

```
AAlignAI/
│
├── backend/
│   ├── app.py                     
│   ├── requirements.txt           
│   └── utils/
│       ├── parser.py              
│       ├── scoring.py             
│       └── helpers.py             
│
├── frontend/
│   ├── index.html                 
│   ├── login.html                 
│   ├── splash.html                
│   ├── css/
│   │   ├── style.css              
│   │   ├── login.css              
│   │   └── splash.css             
│   │
│   ├── js/
│   │   ├── auth.js                
│   │   ├── script.js              
│   │   
│   │
│   └── assets/
│       ├── fonts/                 
│       ├── icons/                
│       ├── logo.svg               
│       ├── splash-animation.json  
│       └── backgrounds/           
│
├── .env                           
├── supabase/
│   ├── schema.sql                 
│   └── supabase.config.json       
│
└── README.md
```

---

## 📌 Use Cases

* Resume screening for job seekers
* Resume optimization and feedback
* HR or recruiter pre-screening tool
* Career counseling and portfolio building

---

## 🗺️ To-Do (Upcoming Features)

* [ ] User login system (Supabase or Firebase)
* [ ] PDF/CSV export of analysis report
* [ ] Resume improvement suggestions via GPT
* [ ] Real-time history tracking and dashboard

---

## 🙌 Acknowledgments

* Built by [Devansh Rai](https://github.com/idevanshrai)
* SentenceTransformers by SBERT
* Inspired by real-world resume challenges

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---
