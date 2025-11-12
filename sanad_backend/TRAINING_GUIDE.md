# Training Guide: Fine-tuning a Mental Health Chatbot Model

## Current System
The current system uses:
- **Sentiment Analysis**: DistilBERT-based sentiment model
- **Rule-based Responses**: Context-aware therapeutic responses
- **Keyword Detection**: Mental health condition identification

## Option 1: Fine-tune a Language Model (Recommended)

### Using Hugging Face Transformers

#### Step 1: Prepare Your Dataset
You'll need a dataset of mental health conversations. Format:
```json
{
  "conversations": [
    {
      "user": "I have depression",
      "therapist": "I understand you're experiencing depression. This is a real medical condition. Can you tell me more about how long you've been feeling this way?"
    },
    {
      "user": "I've been feeling sad for months",
      "therapist": "That sounds really difficult. Depression can persist for extended periods. What have you tried so far to help manage these feelings?"
    }
  ]
}
```

#### Step 2: Choose a Base Model
- **GPT-2** (smaller, faster)
- **DialoGPT** (conversational)
- **LLaMA-2** (if you have access)
- **Mistral-7B** (good balance)

#### Step 3: Fine-tuning Script
```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Load your dataset
dataset = load_dataset("json", data_files="mental_health_dataset.json")

# Load model and tokenizer
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Training arguments
training_args = TrainingArguments(
    output_dir="./sanad-mental-health-model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=1000,
    save_total_limit=2,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)
trainer.train()
```

## Option 2: Use OpenAI API (Easiest, but requires API key)

```python
import openai

def get_therapeutic_response(user_message, context):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compassionate, expert mental health therapist. Provide evidence-based, therapeutic responses. Always prioritize safety."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content
```

## Option 3: Use Pre-trained Mental Health Models

### Available Models:
1. **MentalRoBERTa** - Fine-tuned RoBERTa for mental health
2. **PsychBERT** - Psychology-focused BERT
3. **MentalBERT** - Mental health domain BERT

```python
from transformers import pipeline

mental_health_classifier = pipeline(
    "text-classification",
    model="mental/mental-bert-base-uncased"
)
```

## Option 4: Create Your Own Dataset

### Sources for Mental Health Data:
1. **Reddit**: r/depression, r/anxiety, r/mentalhealth (with proper anonymization)
2. **Mental Health Forums**: 7 Cups, Mental Health America
3. **Therapy Transcripts**: Public domain therapy session transcripts
4. **Clinical Guidelines**: Convert treatment protocols into conversational format

### Dataset Requirements:
- **Minimum**: 1,000 conversation pairs
- **Recommended**: 10,000+ conversation pairs
- **Quality**: Expert-reviewed therapeutic responses
- **Diversity**: Cover multiple conditions (depression, anxiety, trauma, etc.)

## Implementation Steps

### 1. Data Collection & Cleaning
```python
# Example data cleaning
def clean_conversation_data(raw_data):
    # Remove PII
    # Anonymize
    # Format consistently
    pass
```

### 2. Fine-tuning Process
```bash
# Install requirements
pip install transformers datasets torch accelerate

# Run training
python train_mental_health_model.py \
    --model_name gpt2 \
    --dataset_path ./data/mental_health_dataset.json \
    --output_dir ./models/sanad-therapist \
    --epochs 5
```

### 3. Integration
Update `ai_service.py` to use your fine-tuned model:
```python
from transformers import pipeline

therapeutic_model = pipeline(
    "text-generation",
    model="./models/sanad-therapist",
    max_length=200,
    temperature=0.7
)
```

## Best Practices

1. **Safety First**: Always include crisis detection
2. **Ethical Guidelines**: Follow mental health AI ethics
3. **Professional Oversight**: Have mental health professionals review responses
4. **Continuous Improvement**: Regularly update based on feedback
5. **Transparency**: Clearly state AI limitations to users

## Resources

- **Hugging Face**: https://huggingface.co/models
- **Mental Health Datasets**: 
  - Dreaddit (Reddit mental health posts)
  - Mental Health FAQ datasets
- **Training Tutorials**: Hugging Face Transformers course

## Next Steps

1. Collect/curate mental health conversation dataset
2. Choose base model (start with GPT-2 or DialoGPT)
3. Fine-tune on your dataset
4. Evaluate with mental health professionals
5. Integrate into current system
6. A/B test with users

