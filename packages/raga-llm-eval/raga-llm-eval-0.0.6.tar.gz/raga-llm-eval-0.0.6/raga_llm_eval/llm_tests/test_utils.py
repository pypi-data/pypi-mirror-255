from typing import List
from dotenv import load_dotenv
import os
import openai
import spacy

load_dotenv() 
openai.api_key= os.getenv("OPENAI_API_KEY")

nlp = None

def analyze_words(pos_words, sentence):
    global nlp 
    
    if nlp is None:
        nlp = spacy.load('en_core_web_lg') 
    doc = nlp(sentence)

    # Prepare the inputs
    input_dict = {word.split('_')[0]: word.split('_')[1] for word in pos_words}

    # Lemmatization and POS matching
    found_words = [tok.lemma_ for tok in doc if tok.lemma_ in input_dict.keys()]
    found_pos_words = [tok.lemma_+"_"+tok.pos_ for tok in doc if tok.lemma_ in input_dict.keys() and input_dict[tok.lemma_].lower() in tok.pos_.lower()]
    
    # take unique items 
    found_words = list(set(found_words))
    found_pos_words = list(set(found_pos_words))
    return found_words, found_pos_words


def concept_list_str(concept_set):
    concept_strs = []
    for concept in concept_set:
        concept_strs.append(concept.replace("_N", "(noun)").replace("_V", "(verb)"))
    return ", ".join(concept_strs)


def openai_chat_request(
    model:str="gpt-3.5-turbo",
    temperature: float=0,
    max_tokens: int=512,
    top_p: float=1.0,
    frequency_penalty: float=0,
    presence_penalty: float=0,
    prompt: str=None,
    n: int=1,
    messages: List[dict]=None,
    stop: List[str]=None,
    **kwargs,
) -> List[str]:
    """
    Request the evaluation prompt from the OpenAI API in chat format.
    Args:
        prompt (str): The encoded prompt.
        messages (List[dict]): The messages.
        model (str): The model to use.
        engine (str): The engine to use.
        temperature (float, optional): The temperature. Defaults to 0.7.
        max_tokens (int, optional): The maximum number of tokens. Defaults to 800.
        top_p (float, optional): The top p. Defaults to 0.95.
        frequency_penalty (float, optional): The frequency penalty. Defaults to 0.
        presence_penalty (float, optional): The presence penalty. Defaults to 0.
        stop (List[str], optional): The stop. Defaults to None.
    Returns:
        List[str]: The list of generated evaluation prompts.
    """
    # Call openai api to generate aspects
    assert prompt is not None or messages is not None, "Either prompt or messages should be provided."
    if messages is None:
        messages = [{"role":"system","content":"You are an AI assistant that helps people find information."},
                {"role":"user","content": prompt}]
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        n=n,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        **kwargs
    )
    contents = []
    for choice in response['choices']:
        # Check if the response is valid
        if choice['finish_reason'] not in ['stop', 'length']:
            raise ValueError(f"OpenAI Finish Reason Error: {choice['finish_reason']}")
        contents.append(choice['message']['content'])

    return contents