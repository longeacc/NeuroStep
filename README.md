# NeuroStep

**A searchable catalogue of digital tools that help people with acquired brain injury or brain tumours compensate for cognitive difficulties.**

*Catalogue numérique d'applications et d'outils pour cérébrolésés et personnes atteintes de tumeurs cérébrales.*

![Python](https://img.shields.io/badge/Python-3.10%2B-24292e?logo=python&logoColor=auto)
![Streamlit](https://img.shields.io/badge/Streamlit-24292e?logo=streamlit&logoColor=auto)

NeuroStep started at the **SN@SU Hackathon** (Sorbonne Université). Occupational therapists and patients can find apps for communication, memory and planning without searching app stores one by one: each tool is listed, classified by disorder and theme, and searchable.

## What it does

| Feature | Description |
|---|---|
| **Catalogue** | Lists cognitive compensation tools such as communication aids, memory aids and planning tools |
| **Classification** | Each tool is linked to the disorders it addresses and to a theme |
| **Search** | Filter the catalogue by disorder, theme or keyword |
| **Admin interface** | Add, edit and remove entries without touching the data file |

## Architecture

The MVP is a Streamlit application backed by a JSON file, which keeps the data easy to read, edit and extend without a SQL server.

| Path | Role |
|---|---|
| `app.py` | Streamlit application: user view and admin view |
| `database.py` | Manager for the JSON database |
| `data/database.json` | Listed applications, disorders and themes |
| `backend/`, `frontend/` | Work in progress towards an API backend and a web frontend |
| `.github/workflows/` | Continuous integration |

The catalogue stores tools, disorders and themes only. It holds no patient data.

## Quick start

```bash
git clone https://github.com/longeacc/NeuroStep.git
cd NeuroStep

python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

## Roadmap

- Replace the JSON file with a relational database
- Expose the catalogue through an authenticated API
- Add a web frontend usable on phones and tablets
- Improve search so that a therapist can describe a need in plain language

## License

© 2026 Clément Longeac. All rights reserved. The code is public so that the application can be deployed on Streamlit Community Cloud. Copying, modifying, redistributing or reusing it requires written permission, see [LICENSE](LICENSE).

## Contact

Clément Longeac, ESIEE Paris · [LinkedIn](https://www.linkedin.com/in/clément-longeac) · [Email](mailto:clement.longeac@edu.esiee.fr)
