# `text_analysis_model.py` Documentation

## Overview
This file implements a sentiment analysis model for customer chat conversations. It uses a pre-trained DistilBERT model from Hugging Face to classify text as positive or negative sentiment. This is one of the three analysis components in the Customer Churn Prediction System.

## Dependencies
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face transformers library for NLP models
- **DistilBERT**: Lightweight BERT variant fine-tuned for sentiment analysis
- **re**: Regular expressions for text parsing
- **logging**: For application event logging

## Model Details

### Pre-trained Model
The model uses "distilbert-base-uncased-finetuned-sst-2-english", which is:
- A lightweight, distilled version of BERT (33% smaller, 40% faster)
- Fine-tuned on the Stanford Sentiment Treebank v2 (SST-2) dataset
- Pre-trained for binary sentiment classification (positive/negative)

## Main Functions

### `predict_chat(chat_file_paths)`
The main function that processes chat files and predicts sentiment.

#### Parameters:
- `chat_file_paths`: List of paths to text files containing chat conversations

#### Process:
1. **Validate Input**:
   ```python
   if not chat_file_paths:
       logger.info("No chat files were uploaded")
       return "No chat files to process"
   ```

2. **Extract User Messages**:
   ```python
   user1_messages = []
   for file_path in chat_file_paths:
       # Open and read chat files
       # Extract messages matching the pattern ".*? - user1: (.*)"
   ```
   
3. **Combine Messages**:
   ```python
   extracted_text = " ".join(user1_messages)
   ```
   
4. **Fallback for Empty Input**:
   ```python
   if not extracted_text.strip():
       logger.warning("No valid chat messages found in provided files, using default text")
       extracted_text = "The quick brown fox jumps over the lazy dog."
   ```

5. **Initialize Model**:
   ```python
   tokenizer = DistilBertTokenizer.from_pretrained(
       "distilbert-base-uncased-finetuned-sst-2-english"
   )
   model = DistilBertForSequenceClassification.from_pretrained(
       "distilbert-base-uncased-finetuned-sst-2-english"
   )
   ```

6. **Tokenize and Predict**:
   ```python
   inputs = tokenizer(required_text, return_tensors="pt")
   with torch.no_grad():
       logits = model(**inputs).logits
   ```
   
7. **Return Classification**:
   ```python
   predicted_class_id = logits.argmax().item()
   output = model.config.id2label[predicted_class_id]
   return output
   ```

#### Return Value:
- `"POSITIVE"` or `"NEGATIVE"` sentiment classification

## Chat File Format
The expected format for chat files is:
```
timestamp - user1: message
timestamp - user2: response
```

The module specifically extracts and analyzes messages from "user1" (the customer) to determine their sentiment.

## Error Handling
- Handles missing or empty files
- Logs errors when file reading fails
- Provides fallback text if no valid messages are found

## Integration
This module is called from the main application's `upload_files()` function to analyze chat files as part of the multi-modal churn prediction system.