---
tags:
- setfit
- sentence-transformers
- text-classification
- generated_from_setfit_trainer
widget:
- text: 'can u update address for order #67890 smart gadget sent it to wrong place'
- text: 'amazing experience always but this toy order #09876 isnt what my kid wanted
    can u help with a return'
- text: 'Greetings! I received my ''Aero-Fit Wireless Earbuds'' (Order #AF1234, delivered
    April 1, 2024) and unfortunately, the left earbud isn''t charging. I''m a big
    fan of your tech, so I''m keen to get a working pair. What are my options for
    an exchange?'
- text: 'The post-purchase survey I received on November 29, 2023, after my ''PetCare
    Grooming Kit'' purchase (Order #10101) was excessively long and intrusive. It
    felt like harassment. I demand to be removed from all future mailing lists and
    surveys immediately. Stop annoying your customers!'
- text: 'To Whom It May Concern,

    Our project schedule dictates an urgent need for 50 units of the ''Industrial
    Grade Power Supply'' (Model No: IGP-2000). While current stock may be limited,
    could you urgently confirm if a shipment arriving by April 20, 2024 can fulfill
    this requirement?

    Respectfully,

    [Customer Name]'
metrics:
- accuracy
pipeline_tag: text-classification
library_name: setfit
inference: true
base_model: sentence-transformers/all-MiniLM-L6-v2
model-index:
- name: SetFit with sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: text-classification
      name: Text Classification
    dataset:
      name: Unknown
      type: unknown
      split: test
    metrics:
    - type: accuracy
      value: 0.79
      name: Accuracy
---

# SetFit with sentence-transformers/all-MiniLM-L6-v2

This is a [SetFit](https://github.com/huggingface/setfit) model that can be used for Text Classification. This SetFit model uses [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) as the Sentence Transformer embedding model. A [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance is used for classification.

The model has been trained using an efficient few-shot learning technique that involves:

1. Fine-tuning a [Sentence Transformer](https://www.sbert.net) with contrastive learning.
2. Training a classification head with features from the fine-tuned Sentence Transformer.

## Model Details

### Model Description
- **Model Type:** SetFit
- **Sentence Transformer body:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Classification head:** a [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance
- **Maximum Sequence Length:** 256 tokens
- **Number of Classes:** 5 classes
<!-- - **Training Dataset:** [Unknown](https://huggingface.co/datasets/unknown) -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Repository:** [SetFit on GitHub](https://github.com/huggingface/setfit)
- **Paper:** [Efficient Few-Shot Learning Without Prompts](https://arxiv.org/abs/2209.11055)
- **Blogpost:** [SetFit: Efficient Few-Shot Learning Without Prompts](https://huggingface.co/blog/setfit)

### Model Labels
| Label    | Examples                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Happy    | <ul><li>"A very good day to you! I'm inquiring about the whereabouts of order #21314 for 'Designer Sunglasses' purchased May 6th. It hasn't reached my address. Could you provide any details? Appreciatively!"</li><li>'My account access is restored! I was completely locked out. Massive relief, thank you for the speedy assistance!'</li><li>"Hello! I want to give positive feedback for 'Serenity Tea Set'. Order #10018, delivered 2023-12-28. It is very beautiful and make my tea time special. A truly lovely set, very good."</li></ul>                                                                                                                                                                                                                                                                  |
| Urgent   | <ul><li>"Not only do I want a full refund for the 'Gaming Console' (Order #G12345) delivered October 10th, which is clearly a refurbished unit, but I also expect compensation for my wasted time and ruined weekend. This is an absolute outrage!"</li><li>"My order status hasn't changed. Why?"</li><li>'Order #10102 is critically delayed. Provide all details of its current status now.'</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                             |
| Confused | <ul><li>"The shoes, order #ZAB234. They were supposed to arrive on September 10th. I keep checking my door. Nothing. The website says 'out for delivery'. How long does 'out for delivery' take? Is it just driving around?"</li><li>'My Electric Kettle Deluxe, Order #12309, bought on March 1st, is not heating water anymore. Why isnt it working? It literally just stopped. This is incredibly inconvenient and unacceptable. I will be sure to tell everyone I know not to buy from your company if this isnt sorted out immediately.'</li><li>'My subscription for Cloud Service was cancel last month. But I see a new charge on Oct 25 for this. What is this charge? I did not want renew.'</li></ul>                                                                                                      |
| Angry    | <ul><li>"Oh, wonderful! My 'new' product arrived with obvious signs of prior use. A lovely commitment to quality control."</li><li>"Dear Support, I am merely touching base concerning the 'solution' provided for my email synchronization issues, account #EMAIL404. I find it somewhat amusing that your fix has, in fact, made the problem worse. I had hoped for an improvement, not further complications. Please revisit this issue with greater diligence."</li><li>"This is an outrage! Your company's quality control is a joke. The 'Premium Widget' I purchased last week is already failing. I expect a full refund and an explanation, or I will be taking my concerns to a lawyer regarding false advertising. I will never patronize your business again after this horrendous experience."</li></ul> |
| Neutral  | <ul><li>'shipping for order #55667 is to old address please send to my new one'</li><li>"Your customer service has been completely unhelpful regarding my return for the 'Professional Hair Dryer' (Order #1011) from November 11, 2024. I demand a full refund and for this entire situation to be escalated to someone who actually knows how to do their job."</li><li>"Good morning. This isn't urgent at all, so take your time. I just wanted to ask if the widget I bought on the 5th should be making that whirring noise. It's not a huge concern, just new."</li></ul>                                                                                                                                                                                                                                      |

## Evaluation

### Metrics
| Label   | Accuracy |
|:--------|:---------|
| **all** | 0.79     |

## Uses

### Direct Use for Inference

First install the SetFit library:

```bash
pip install setfit
```

Then you can load this model and run inference.

```python
from setfit import SetFitModel

# Download from the 🤗 Hub
model = SetFitModel.from_pretrained("setfit_model_id")
# Run inference
preds = model("can u update address for order #67890 smart gadget sent it to wrong place")
```

<!--
### Downstream Use

*List how someone could finetune this model on their own dataset.*
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Set Metrics
| Training set | Min | Median | Max |
|:-------------|:----|:-------|:----|
| Word count   | 4   | 53.928 | 204 |

| Label    | Training Sample Count |
|:---------|:----------------------|
| Angry    | 100                   |
| Confused | 100                   |
| Happy    | 100                   |
| Neutral  | 100                   |
| Urgent   | 100                   |

### Training Hyperparameters
- batch_size: (16, 16)
- num_epochs: (1, 1)
- max_steps: -1
- sampling_strategy: oversampling
- num_iterations: 20
- body_learning_rate: (2e-05, 2e-05)
- head_learning_rate: 2e-05
- loss: CosineSimilarityLoss
- distance_metric: cosine_distance
- margin: 0.25
- end_to_end: False
- use_amp: False
- warmup_proportion: 0.1
- l2_weight: 0.01
- seed: 42
- eval_max_steps: -1
- load_best_model_at_end: False

### Training Results
| Epoch  | Step | Training Loss | Validation Loss |
|:------:|:----:|:-------------:|:---------------:|
| 0.0008 | 1    | 0.561         | -               |
| 0.04   | 50   | 0.3172        | -               |
| 0.08   | 100  | 0.2511        | -               |
| 0.12   | 150  | 0.2279        | -               |
| 0.16   | 200  | 0.2025        | -               |
| 0.2    | 250  | 0.1872        | -               |
| 0.24   | 300  | 0.15          | -               |
| 0.28   | 350  | 0.1307        | -               |
| 0.32   | 400  | 0.123         | -               |
| 0.36   | 450  | 0.0949        | -               |
| 0.4    | 500  | 0.0675        | -               |
| 0.44   | 550  | 0.0545        | -               |
| 0.48   | 600  | 0.0428        | -               |
| 0.52   | 650  | 0.0323        | -               |
| 0.56   | 700  | 0.0263        | -               |
| 0.6    | 750  | 0.0172        | -               |
| 0.64   | 800  | 0.0136        | -               |
| 0.68   | 850  | 0.0108        | -               |
| 0.72   | 900  | 0.0078        | -               |
| 0.76   | 950  | 0.0082        | -               |
| 0.8    | 1000 | 0.0069        | -               |
| 0.84   | 1050 | 0.0068        | -               |
| 0.88   | 1100 | 0.0065        | -               |
| 0.92   | 1150 | 0.0053        | -               |
| 0.96   | 1200 | 0.0056        | -               |
| 1.0    | 1250 | 0.0051        | -               |

### Framework Versions
- Python: 3.12.12
- SetFit: 1.1.3
- Sentence Transformers: 5.1.2
- Transformers: 4.57.2
- PyTorch: 2.9.0+cu126
- Datasets: 4.0.0
- Tokenizers: 0.22.1

## Citation

### BibTeX
```bibtex
@article{https://doi.org/10.48550/arxiv.2209.11055,
    doi = {10.48550/ARXIV.2209.11055},
    url = {https://arxiv.org/abs/2209.11055},
    author = {Tunstall, Lewis and Reimers, Nils and Jo, Unso Eun Seo and Bates, Luke and Korat, Daniel and Wasserblat, Moshe and Pereg, Oren},
    keywords = {Computation and Language (cs.CL), FOS: Computer and information sciences, FOS: Computer and information sciences},
    title = {Efficient Few-Shot Learning Without Prompts},
    publisher = {arXiv},
    year = {2022},
    copyright = {Creative Commons Attribution 4.0 International}
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->