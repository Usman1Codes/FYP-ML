# JUNO Automation Engine

A robust, hybrid AI engine for automated customer support. It combines Machine Learning for intent classification with a deterministic rule-based engine for safe, accurate data retrieval.

---

## 📂 Project Structure & File Purpose

| Directory | File Name | Description |
| :--- | :--- | :--- |
| **Root** | `juno_engine.py` | **The Brain.** Main script running the entire pipeline (AI + Logic). |
| | `requirements.txt` | **Dependencies.** Python libraries required to run the engine. |
| **Config** | `intent-variable.json` | **The Rules.** Defines required entities (e.g., order_id) for each intent. |
| | `mock-database.json` | **The Data.** Simulated backend with fake customer orders & products. |
| | `reponse-templates.json` | **The Voice.** Pre-written templates for all response scenarios. |
| **Models** | `intent_classifier.joblib` | **The AI.** Machine Learning model predicting customer intent. |
| | `label_encoder.joblib` | **The Decoder.** Converts model output (numbers) back to text labels. |

---

## 🚀 Setup & Execution

### 1. Environment Setup

```bash
cd ~/FYP/ML
```

### 2. Install Requirements
```
pip install -r requirements.txt
```
### 3. Run the Engine
```
python juno_engine.py
```

## 🌊 The Logic Flow (How It Works)

### 1. Input & Classification (AI Layer)
User asks: "Where is order #123?"

AI model (Sentence Transformer + Logistic Regression) analyzes meaning.

Output:

Intent: order_status_inquiry

Confidence: 98%

### 2. Configuration Lookup (Rule Layer)
Loads intent-variable.json

Learns required entities for order_status_inquiry:

order_id

### 3. Entity Extraction (Mining Layer)
Scans user message with:

Regex patterns

Mock database lookups

Finds order reference: #12345

### 4. State Management (Decision Layer)
Compares required entities vs extracted entities

Logic:

Missing → missing_info

Found → query mock-database.json

Database result:

Order #12345 → Status: Shipped

### 5. Response Generation (Output Layer)
Loads appropriate template from:

reponse-templates.json

Fills response:

"Great news. Order #12345 is Shipped."

