import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os
import re
import logging

logger = logging.getLogger(__name__)

def predict_chat(chat_file_paths):
    if not chat_file_paths:
        logger.info("No chat files were uploaded")
        return "No chat files to process"
    
    user1_messages = []
    for file_path in chat_file_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.readlines()
                    for line in file_content:
                        user1_match = re.search(r'.*? - user1: (.*)', line)
                        if user1_match:
                            message = user1_match.group(1).strip()
                            user1_messages.append(message)
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
    
    extracted_text = " ".join(user1_messages)
    
    if not extracted_text.strip():
        logger.warning("No valid chat messages found in provided files, using default text")
        extracted_text = "The quick brown fox jumps over the lazy dog."

    tokenizer = DistilBertTokenizer.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )

    required_text = extracted_text

    inputs = tokenizer(required_text, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = logits.argmax().item()
    output = model.config.id2label[predicted_class_id]
    return output
