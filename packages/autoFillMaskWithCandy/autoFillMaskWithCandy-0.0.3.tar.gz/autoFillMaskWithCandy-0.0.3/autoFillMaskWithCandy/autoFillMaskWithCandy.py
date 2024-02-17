import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForMaskedLM

# function to set you model from hugging face as the model and tokenizer
def setTokenModel(model_name):
    global tokenizer, model, mask_token
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    mask_token = tokenizer.mask_token
    #print(mask_token)

# function to automatically mask differing words
def mask_differing_words(input_sentences):
    # Tokenize the input sentences
    tokenized_sentences = [sentence.split() for sentence in input_sentences]

    # Find differing words
    differing_words = set()
    for i in range(len(tokenized_sentences[0])):
        for j in range(1, len(tokenized_sentences)):
            if tokenized_sentences[0][i] != tokenized_sentences[j][i]:
                differing_words.add((i, tokenized_sentences[0][i]))

    # Organize differing words by their index
    differing_words = sorted(list(differing_words), key=lambda x: x[0])

    # Mask differing words in each sentence
    masked_inputs = []
    for sentence_tokens in tokenized_sentences:
        masked_tokens = sentence_tokens.copy()
        for index, word in differing_words:
            masked_tokens[index] = mask_token  # --> changes [MASK] to mask_token
        masked_inputs.append(" ".join(masked_tokens))

    # Create candidates list for each differing word
    candidates_list = [[] for _ in differing_words]
    for k, (index, word) in enumerate(differing_words):
        candidates = set()
        for sentence_tokens in tokenized_sentences:
            candidates.add(sentence_tokens[index])
        candidates_list[k] = list(candidates)

    unique_masked_inputs = list(set(masked_inputs))

    return unique_masked_inputs, candidates_list

# function to calculate the probability of a candidate
def get_candidate_probability(candidate, mask_index, tokenized_text):
    # Directly tokenize the candidate (expecting candidate to be a string)
    candidate_tokens = tokenizer.tokenize(candidate)

    # Prepare the input with the candidate token(s) in place of the mask
    tokenized_text_with_candidate = tokenized_text[:mask_index] + candidate_tokens + tokenized_text[mask_index+1:]
    
    # Convert the updated token list to IDs and proceed as before
    input_ids = tokenizer.convert_tokens_to_ids(tokenized_text_with_candidate)
    input_tensor = torch.tensor([input_ids])

    # Get model predictions
    with torch.no_grad():
        outputs = model(input_tensor)
        logits = outputs.logits

    # Focus on the logits for the masked position; this assumes mask_index is adjusted for tokenized input
    mask_logits = logits[0, mask_index]

    # Apply softmax to get probabilities
    mask_probs = softmax(mask_logits, dim=0)

    # Assuming candidate_tokens[0] is the main token for the candidate
    candidate_id = tokenizer.convert_tokens_to_ids([candidate_tokens[0]])[0]
    candidate_prob = mask_probs[candidate_id].item()

    return candidate_prob

#funtion to show the masked input and provide the scores 
def show_mask_fill(input_sentences):
    unique_masked_inputs, candidates_list = mask_differing_words(input_sentences)

    # tokenize the input sentence
    tokenized_text = tokenizer.tokenize(unique_masked_inputs[0])
    mask_token_indices = [i for i, token in enumerate(tokenized_text) if token == mask_token] # --> changes [MASK] to mask_token

    print(f"Masked Input: {unique_masked_inputs[0]}\n")

    # evaluating the probability of each candidate word for each mask
    for mask_index, candidates in zip(mask_token_indices, candidates_list):
        for candidate in candidates:
            # Ensure candidate is a string; no need to tokenize here since it's done inside get_candidate_probability
            candidate_probability = get_candidate_probability(candidate, mask_index, tokenized_text)
            print(f"Mask {mask_index + 1}, {candidate:<20} {candidate_probability}")


def mask_fill_replaced(input_sentences):
    unique_masked_inputs, candidates_list = mask_differing_words(input_sentences)

    for input_sentence in unique_masked_inputs:
        # Tokenize the input sentence
        tokenized_text = tokenizer.tokenize(input_sentence)
        # Find indices of masked tokens
        mask_token_indices = [i for i, token in enumerate(tokenized_text) if token == mask_token] # --> changes [MASK] to mask_token

    # Create a copy of the original tokenized text
    replaced_text = tokenized_text.copy()

    # Evaluate the probability of each candidate word for each mask
    for mask_index, candidates in zip(mask_token_indices, candidates_list):
        # Find the candidate with the highest probability
        best_candidate = max(candidates, key=lambda candidate: get_candidate_probability(candidate, mask_index, tokenized_text))
        # Replace the mask with the best candidate in the copied text
        replaced_text[mask_index] = best_candidate

    # Join tokens to form complete words
    replaced_sentence = tokenizer.convert_tokens_to_string(replaced_text)

    #print(f"Original Sentence: {input_sentence}")

    # Print the replaced sentence
    #print(f"{replaced_sentence}")

    return replaced_sentence

'''
input_sentences = [
    "Pasensya heto lng ako, bobo sa pagaral",
    "Pasensya hito lng ako, bobo sa pagaral",
    "Pasensya heto lng ako, bubo sa pagaral",
    "Pasensya hito lng ako, bubo sa pagaral"
]
modelInput=("GKLMIP/bert-tagalog-base-uncased")
setTokenModel(modelInput)
show_mask_fill(input_sentences)
print(f"\n{mask_fill_replaced(input_sentences)}")'''

