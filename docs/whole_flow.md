
## 1. High-Level Flow Summary
The system follows a linear pipeline with a recursive "Slot-Filling Loop." It ingests emails, determines intent/mood via ML, and routes them to one of two paths:
1.  **Direct Answer (FAQ):** Matches against a vendor-defined knowledge base.
2.  **Transactional (Order/Product/Stock):** Checks for required data fields. If data is missing, it enters a recursive loop asking the user for details using Jinja2 templates. If data is complete, it queries the database and sends a templated resolution.

All outgoing emails pass through a **Gemini Compliance Layer** for final safety vetting.

---

## 2. End-to-End Logic Workflow

### Phase 1: Ingestion & Intelligence (The ML Layer)
Every incoming email ($X$) is processed by the ML Engine to extract three metadata points. This results in a "Ticket Object" creation.

1.  **Intent Classification (Probability-Based):**
    * The model predicts the probability of the 4 supported intents.
    * **Requirement:** The demo UI must visually display these confidence scores (e.g., *Order Status: 92%, FAQ: 5%*).
2.  **Mood Detection:**
    * Classifies the emotional tone into fixed categories: `[Neutral, Angry, Happy, Confused]`.
    * This label allows the Jinja template to swap in empathetic phrases later.
3.  **Entity Extraction (NER):**
    * Scans $X$ for specific fields defined in the Intent Schema (e.g., Order IDs, SKUs, Phone Numbers).

### Phase 2: The Routing Logic (The Fork)

Once the intent is locked, the system branches:

#### Branch A: The General FAQ Path
*Logic:* This intent requires **no** external database processing and **no** slot filling.
1.  **Lookup:** The system takes the user's question and performs a semantic search against the specific Vendor's FAQ dashboard entries.
2.  **Drafting:** It retrieves the pre-written answer set by the vendor.
3.  **Mood Injection:** The answer is wrapped in a Jinja template that adjusts the opening/closing based on the detected Mood (e.g., if `Angry`, add priority apology).
4.  **Next Step:** Proceed to **Phase 5 (Compliance)**.

#### Branch B: The Transactional Path (Order / Product / Stock)
*Logic:* These intents require specific data to run a backend query.

**Step 1: The Completeness Check**
The system compares the `Extracted_Entities` against the `Required_Fields` for that specific intent.

**Step 2: The Slot-Filling Loop (Recursive)**
* **IF Fields Are Missing:**
    1.  **Action:** The system selects the **"Request Info Template"** (Jinja2).
    2.  **Dynamic Content:** The template dynamically inserts questions *only* for the missing fields.
    3.  **Mood Handling:** The template adjusts tone based on detected mood.
    4.  **State:** Ticket Status set to `PENDING_CUSTOMER`.
    5.  **Output:** Email sent to user.
    6.  **Loop:** The system waits for a reply. When the reply comes, it is treated as a new input ($X$) attached to this ticket, and we re-run NER to see if the missing field is now present. **This loop repeats until all fields are collected.**

* **IF All Fields Are Present:**
    1.  **Action:** Proceed to Phase 3 (Processing).

### Phase 3: Backend Processing (The Resolution)
*Only reachable if Branch B has all required fields.*
1.  **Query Execution:** The system queries the mock E-Commerce Database using the collected fields (e.g., `SELECT status FROM orders WHERE id = [Order_ID]`).
2.  **Result Retrieval:** The DB returns the raw answer (e.g., "Shipped", "Out of Stock").

### Phase 4: Response Generation (Jinja2)
The system selects the **"Final Reply Template"** for the specific intent.
* **Input:** DB Results + User Name + Mood.
* **Process:** Jinja2 renders the final email body.
* *Note:* The Vendor configures this template structure, but cannot delete the logic placeholders for the DB results.

### Phase 5: The Compliance Layer (Gemini)
* **Input:** The fully rendered draft email from Phase 4 (or Phase 2 FAQ).
* **Task:** Vetting ONLY. Gemini does not write the email.
* **Prompt:** "Verify this email allows for context and compliance. Ensure no PII leaks and tone is appropriate. Output: PASS or FAIL."
* **Output:** If PASS, send email via SMTP.

---

## 3. Detailed Use-Case Definitions

### 1. Order Status Inquiries
* **Intent:** "Where is my order?"
* **Required Fields:** `Order Number`, `Customer Verification` (Email or Phone).
* **Action:** Query DB `Orders` table.
* **Outcome:** Reply with current shipping status and tracking link.

### 2. Product Information / Inquiries
* **Intent:** Specific questions about product specs/features.
* **Required Fields:** `Product Name` or `SKU`.
* **Action:** Query DB `Products` table for specifications.
* **Outcome:** Reply with the specific product details requested.

### 3. Inventory / Stock Availability
* **Intent:** "Is this item in stock?"
* **Required Fields:** `Product Name` or `SKU`, `Size/Variant` (if applicable).
* **Action:** Query DB `Inventory` table.
* **Outcome:** Reply with "In Stock" (and quantity) or "Out of Stock" (with restock date if available).

### 4. General FAQ Questions
* **Intent:** Return policy, Store hours, Shipping regions.
* **Required Fields:** None.
* **Action:** Internal Semantic Match against Vendor Dashboard Knowledge Base.
* **Outcome:** Direct reply based on the stored answer.

---

## 4. Vendor Dashboard Specifications

The dashboard is the control center. It must feature the following **Ticket Management** capabilities:

### A. Advanced Filtering System
The Vendor must be able to slice the ticket view using three distinct toggles:
1.  **Filter by Use-Case:** `[Show All | Order Status | Product Info | Inventory | FAQ]`
2.  **Filter by Status:** `[Action Required | Pending Customer Reply | Resolved]`
    * *Pending Customer Reply:* Means the system is currently in the "Slot-Filling Loop" waiting for the user.
    * *Action Required:* Means the AI failed or needs manual approval.
3.  **Filter by Mood:** `[Neutral | Angry | Happy | Urgent]`
    * *Use Case:* Allows vendors to prioritize "Angry" customers first.

### B. Template Management
* **Configuration:** Vendors can edit the Jinja2 templates for both "Request Info" and "Final Reply."
* **Safety:** The UI must prevent the vendor from deleting critical variable blocks (e.g., `{{ order_status_result }}`).

---

## 5. Process Flow Diagram (Engineering View)



**(Text Description for Diagram Logic):**
1.  **Start:** Incoming Email.
2.  **Node 1 (ML Engine):** Detect Intent & Mood. Extract Entities.
3.  **Decision Diamond:** Is Intent == FAQ?
    * **YES:** Match FAQ in Knowledge Base -> **Node 4 (Drafting)**.
    * **NO:** Proceed to **Node 2 (Completeness Check)**.
4.  **Node 2 (Completeness Check):** Are all Required Fields for this intent present?
    * **NO (Missing Data):**
        * Generate "Request Info" Email (Jinja + Mood).
        * Send to User.
        * Set Status: `Pending Customer`.
        * **Wait for Reply -> Return to Start (Loop).**
    * **YES (Complete):**
        * Query Database (Backend Processing).
        * Retrieve Data.
        * Proceed to **Node 3 (Final Drafting)**.
5.  **Node 3 (Final Drafting):**
    * Load "Final Reply" Template.
    * Inject DB Data + Mood + User Name.
6.  **Node 4 (Compliance):**
    * Gemini API Check.
    * Pass? -> **Send Email.**
    * Fail? -> **Flag for Human Review.**

---

## 6. Assumptions & Constraints

1.  **No LLM Generation:** We are not using Gemini/GPT to *write* the text to avoid hallucinations. Text is strictly Rule-Based + Jinja Templates.
2.  **Field Immutability:** Vendors cannot add custom required fields to intents (e.g., asking for "Shoe Size" on an Order Status intent) without developer intervention.
3.  **One Intent Per Email:** We assume the customer has one primary goal per email. The highest probability intent wins.
4.  **Dashboard Sync:** Changes made by the Vendor in the dashboard (e.g., updating an FAQ answer) reflect immediately in the next processed email.