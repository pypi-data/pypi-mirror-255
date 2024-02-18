import logging
import random

import pandas as pd

import os
import torch


import openai
openai.api_key = ""


from argparse import ArgumentParser
from joblib import Memory

from sklearn.metrics import accuracy_score, f1_score
from transformers import AdamW, get_linear_schedule_with_warmup
from transformers import BertTokenizer, BertModel,  AutoTokenizer, AutoModelForCausalLM
from transformers import DebertaModel, DebertaTokenizer, GPT2Tokenizer, GPT2Model, GPT2LMHeadModel, DebertaForSequenceClassification
from transformers import OPTConfig, OPTModel, BertForSequenceClassification, AutoModelWithLMHead, LlamaTokenizer, LlamaConfig
from transformers import set_seed
from torch.nn import CrossEntropyLoss
from few_shot_priming.config import *
from few_shot_priming.experiments import *
from few_shot_priming.mylogging import *
from few_shot_priming.argument_sampling.topic_similarity import *
from few_shot_priming.argument_sampling.topic_similarity_sentence_transformer import *
from few_shot_priming.argument_sampling.diversify import *
use_cuda = torch.cuda.is_available()

openai.api_key = get_openai_key()

def save_pre_trained_model():
    """
    Saving pretrained model to use huggingface transformers without internet
    """
    config = load_config()
    config = config["pre-trained-models"]
    path = Path(config["path"])
    bert_path = os.path.join(path,"bert-base-uncased")
    if not os.path.exists(bert_path):
        bert = BertForSequenceClassification.from_pretrained('bert-base-uncased')
        berttokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        bert.save_pretrained(bert_path)
        berttokenizer.save_pretrained(bert_path)


    gpt_2_path = os.path.join(path, "gpt2-xl")
    if not os.path.exists(gpt_2_path):
        gpt_2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
        gpt_2_model = GPT2Model.from_pretrained('gpt2-xl')
        gpt_2_model.save_pretrained(gpt_2_path)
        gpt_2_tokenizer.save_pretrained(gpt_2_path)

    deberta_path = os.path.join(path, "microsoft/deberta-base")
    if not os.path.exists(deberta_path):
        deberta_tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-base")
        deberta_model = DebertaForSequenceClassification.from_pretrained("microsoft/deberta-base")
        deberta_tokenizer.save_pretrained(deberta_path)
        deberta_model.save_pretrained(deberta_path)
    alpaca_path  = os.path.join(path, "wxjiao/alpaca-7b")

    if not os.path.exists(alpaca_path) and torch.cuda.is_available():
        device = torch.device("cpu")
        alpaca_tokenizer = AutoTokenizer.from_pretrained("wxjiao/alpaca-7b")
        alpaca_model = AutoModelForCausalLM.from_pretrained("wxjiao/alpaca-7b", device_map="auto")

        alpaca_tokenizer.save_pretrained(alpaca_path)
        alpaca_model.save_pretrained(alpaca_path)
    geo_neox_path = os.path.join(path, "EleutherAI/gpt-neox-20b")
    if not os.path.exists(geo_neox_path) :

        gptneox_tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")
        gptneox_model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neox-20b").half().cuda()

        gptneox_tokenizer.save_pretrained(geo_neox_path)
        gptneox_model.save_pretrained(geo_neox_path)



    model, tokenizer = add_special_tokens(model, tokenizer, specials_to_add=specials_to_add)

    if 'opt' in model_name:
        tokenizer.add_bos_token=False
    return model, tokenizer, model_config, wrapper

def format_prompt( dataset, tokenizer, labels_text_map, token_limit, few_shot_size, logger, alpaca_examples=False, record=pd.DataFrame({})):
    label_str = ""
    for i, label in enumerate(labels_text_map):
        if i == len(labels_text_map) - 1:
            label_str = label_str + " or " +  labels_text_map[label]
        else:
            label_str = label_str + ", " + labels_text_map[label]
    examples = ""
    if len(record):
        prompt_head = "Given are the following examples:\n"
        prompt_head_2 = f"Classify the stance of the following argument on the given topic into {label_str}: \n"
        prompt = prompt_head + prompt_head_2
        sentence = record["text"]
        topic = record["topic"]

        template_no_stance = f"On the topic '{topic}' the argument '{sentence}' has the stance"
        prompt = prompt + template_no_stance
        record_tokens = tokenizer.encode(prompt)
        record_size = len(record_tokens)
        token_limit = token_limit - record_size - 1 # 1 is added extra for the label to predicted
    token_limit = token_limit // (few_shot_size)
    for i, train_record in dataset.iterrows():
        sentence = train_record["text"]

        id = train_record["id"]
        topic = train_record["topic"]
        stance = train_record["stance"]
        label = labels_text_map[stance]

        if alpaca_examples:
            template = f"""Topic: {topic} \n Argument: {sentence} \n Response: {label}\n"""
        else:
            template = f"On the topic '{topic}' the argument '{sentence}' has the stance {label}.\n"

        tokens = tokenizer.encode(template)
        if len(tokens) > token_limit:
            sentence_tokens = tokenizer.encode(sentence)
            tokens_to_remove_from_sentence = len(tokens) + 1 - token_limit
            if tokens_to_remove_from_sentence < len(sentence_tokens):
                sentence = tokenizer.decode(sentence_tokens[:-tokens_to_remove_from_sentence], skip_special_tokens=True)
            else:
                continue
        if alpaca_examples:
            template = f"""Topic: {topic} \nArgument: {sentence} \n Response: {label}\n"""
        else:
            template = f"On the topic '{topic}' the argument '{sentence}' has the stance {label}.\n"
        assert (len(tokenizer.encode(template))<= token_limit)
        log_message(logger, f"{id}:{token_limit}\tOn the topic '{topic}' the argument '{sentence}' has the stance {label}\t", level=logging.INFO)
        examples = examples + template
    if len(record):
        return prompt_head + examples + prompt_head_2 + template_no_stance
    else:
        return examples


def run_experiment_prompting(config=None, experiment="ibmsc", model=None, offline=False, validate=True, splits=None, logger=None, debug=False, openai=False, topic_count=None, sampling_strategy=None, similarity=None):


    few_shot_size = config["few-shot-size"]
    batch_size = config["batch-size"]
    labels_text_map = {0: "Con", 1: "Pro" ,  2: "Neutral" }
    if not splits:
        if sampling_strategy:
            splits = load_splits(experiment, oversample=False, validate=validate, topic_count= topic_count, debug=debug)
        else:
            splits = load_splits(experiment, oversample=True, validate=validate, topic_count= topic_count, debug=debug)
        if topic_count:
            log_message(logger, f"loading {topic_count} topics got {len(splits['training'])}")
    else:
        training_dataset = splits["training"]

    if validate:
        experiment_type = "validation"
    else:
        experiment_type = "test"
    test_dataset = splits[experiment_type]

    #test_dataset = test_dataset.sample(16)
    if not openai:
        #save_pre_trained_model()
        if offline:
            model_name = config["model-path"]
        else:
            model_name = config["model-name"]
        log_message(logger, f"{model_name} loaded", logging.INFO)
        if "alpaca" in model_name:
            tokenizer = LlamaTokenizer.from_pretrained(model_name)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
        if not model:
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map = 'auto')
        model_is_on_cuda = next(model.parameters()).is_cuda
        log_message(logger,f"model is on cuda {model_is_on_cuda}", logging.INFO)
        if use_cuda and not model_is_on_cuda:
            model= model.cuda()
    else:
        tokenizer = AutoTokenizer.from_pretrained("gpt2")

    model_input_limit = config["model-input-limit"]

    #token_limit = token_limit - template_size

    predictions = []

    labels = []
    log_message(logger, f"** few shot-size {few_shot_size}", logging.INFO)
    if sampling_strategy=="similar":
        log_message(logger, f"** smapling strategy {sampling_strategy}", logging.INFO)
        similarities = load_similarities(experiment=experiment, experiment_type=experiment_type, model=similarity)
    #i = 0
    for i, record in test_dataset.iterrows():


        if not sampling_strategy:
            if few_shot_size > len(splits["training"]):
                training_dataset = splits["training"]
            else:
                training_dataset = splits["training"].sample(few_shot_size)
            training_dataset.sort_values("topic", inplace=True)
        elif sampling_strategy == "similar":
            training_dataset, scores = sample_similar_examples(record["id"], similarities, splits["training"], few_shot_size)
        else:
            training_dataset = sample_diverse_examples(experiment, experiment_type, few_shot_size, logger, topic_count )


        prompt_to_predict = format_prompt(training_dataset, tokenizer, labels_text_map, model_input_limit, few_shot_size, logger, False, record)

        log_message(logger, prompt_to_predict + f" with the id {record['id']}", level=logging.INFO)
        label = record["stance"]
        labels.append(label)
        log_message(logger, f"label {label}", level=logging.INFO)
        if openai:

            completion = prompt_openai("text-davinci-003", prompt_to_predict)
            log_message(logger, completion, logging.INFO)
            resulted_string_truncated = completion[-15:].lower()
        else:
            seq = tokenizer.encode(prompt_to_predict, return_tensors="pt")
            if use_cuda:
                seq = seq.cuda()
            assert(len(seq)<model_input_limit)
            generated = model.generate(seq, max_new_tokens=1, )
            resulting_string = tokenizer.decode(generated.tolist()[0])
            log_message(logger, "***OUTPUT***"+resulting_string[-15:].lower(), level=logging.INFO)
            resulted_string_truncated = resulting_string[-15:].lower()

        if "pro" in resulted_string_truncated :
            predictions.append(1)
        elif "con" in resulted_string_truncated:
            predictions.append(0)
        else:
            predictions.append(2)
        #i = i + 1

    log_message(logger, f"predictions {predictions}", level=logging.WARNING)
    log_message(logger, f"labels {labels}", level=logging.WARNING)
    accuracy = accuracy_score(labels, predictions)
    metrics = {}
    if experiment == "vast":
        f1s = f1_score(labels, predictions, average=None, labels=[0, 1, 2])
        neutral_f1 = f1s[2]
        metrics[f"{experiment_type}/neutral-f1"] = neutral_f1
    else:
        f1s = f1_score(labels, predictions, average=None, labels=[0, 1])
    con_f1 = f1s[0]
    pro_f1 = f1s[1]

    macro_f1 = f1_score(labels, predictions, average="macro")

    metrics[f"{experiment_type}/pro-f1"] = pro_f1
    metrics[f"{experiment_type}/con-f1"] = con_f1
    if experiment == "vast":
        metrics[f"{experiment_type}/neutral-f1"] = neutral_f1

    metrics[f"{experiment_type}/macro-f1"] = macro_f1
    metrics[f"{experiment_type}/accuracy"] = accuracy

    log_metrics(logger, metrics, level=logging.WARNING)
    return metrics

memory = Memory("cachedir")
@memory.cache
def prompt_openai(model, prompt):
    response = openai.Completion.create(model=model,
                                        prompt=prompt,
                                        max_tokens= 1,temperature=0)
    resulted_string_truncated = response["choices"][0]["text"]
    return resulted_string_truncated
