# JUNO Automation Engine

A robust, hybrid AI engine for automated customer support. It combines Machine Learning for intent classification with a deterministic rule-based engine for safe, accurate data retrieval.

---

## 📂 Project Structure & File Purpose

| Directory | File Name | Description |
| :--- | :--- | :--- |
| **src/** | `juno_engine.py` | **The Brain.** Main script running the entire pipeline (AI + Logic). |
| | `data_loader.py` | **Data Loader.** Handles loading JSON configurations and databases. |
| | `intent_classifier.py` | **The AI.** ML model wrapper for intent prediction. |
| | `entity_extractor.py` | **The Miner.** Extracts structured data from text. |
| | `state_manager.py` | **The Brain.** Manages state and executes database lookups. |
| | `response_engine.py` | **The Speaker.** Generates responses using templates. |
| **config/** | `intent_config.json` | **The Rules.** Defines required entities (e.g., order_id) for each intent. |
| | `mock_database.json` | **The Data.** Simulated backend with fake customer orders & products. |
| | `response_templates.json` | **The Voice.** Pre-written templates for all response scenarios. |
| **models/** | `intent_classifier.joblib` | **The AI.** Machine Learning model predicting customer intent. |
| | `label_encoder.joblib` | **The Decoder.** Converts model output (numbers) back to text labels. |
| **data/raw/** | `*.json` | **Training Data.** Original training data JSON files. |
| **notebooks/** | `model_training.ipynb` | **Training Notebook.** Jupyter notebook for model training. |
| **scripts/** | `content_generation.py` | **Content Generator.** Script for generating training data. |
| **docs/** | `conventions.md` | **Conventions.** Project conventions and standards. |
| **Root** | `requirements.txt` | **Dependencies.** Python libraries required to run the engine. |

---

## 🚀 Setup & Execution

### 1. Environment Setup

```bash
cd /path/to/FYP-ML
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the Engine
```bash
python src/juno_engine.py
```

## 🌊 The Logic Flow (How It Works)

### 1. Input & Classification (AI Layer)
User asks: "Where is order #123?"

AI model (Sentence Transformer + Logistic Regression) analyzes meaning.

Output:

Intent: order_status_inquiry

Confidence: 98%

### 2. Configuration Lookup (Rule Layer)
Loads `config/intent_config.json`

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

Found → query `config/mock_database.json`

Database result:

Order #12345 → Status: Shipped

### 5. Response Generation (Output Layer)
Loads appropriate template from:

`config/response_templates.json`

Fills response:

"Great news. Order #12345 is Shipped."

---

## 📚 Additional Resources

- See `docs/conventions.md` for project conventions and coding standards
- Training data is located in `data/raw/`
- Model training notebook: `notebooks/model_training.ipynb`

