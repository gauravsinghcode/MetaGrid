# MetaGrid

MetaGrid is a metadata-driven backend engine that dynamically generates CRUD operations based on database schema, eliminating hardcoded queries and enabling scalable backend systems.

---

## 🚀 Why MetaGrid?

Most backend systems tightly couple logic with database structure.

MetaGrid solves this by:
- Separating schema from execution logic
- Dynamically generating queries using metadata
- Making backend systems reusable and scalable

---

## 🧠 Core Idea

Instead of writing queries manually:

👉 Store table + column metadata  
👉 Build queries dynamically  
👉 Execute via structured pipeline  

---

## 🏗️ Architecture

MetaGrid follows a layered architecture:

          Request
            ↓
        Validation Layer
            ↓
        Metadata Resolution
            ↓
        Query Builder
            ↓
        Execution Engine
            ↓
          Response


---

## ⚙️ Key Features

- Dynamic CRUD operations (no hardcoding)
- Metadata-driven schema handling
- Clean separation of concerns
- Reusable backend logic across tables
- Structured query generation

---

## 🛠 Tech Stack

- Python
- Django
- SQL

---

## 📂 Project Structure

core/
metadata/
validators/
query_builder/
execution/


---

## ▶️ Running the Project

```bash

pip install -r requirements.txt
python manage.py runserver

```

---


