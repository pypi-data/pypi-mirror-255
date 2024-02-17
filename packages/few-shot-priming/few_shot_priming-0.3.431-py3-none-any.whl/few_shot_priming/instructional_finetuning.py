import os
import os.path as osp
import random
import sys
import torch
import transformers
import json
import logging

from datasets import load_dataset
from datasets import Dataset,DatasetDict
from sklearn.metrics import accuracy_score,f1_score
from torch.utils.data import DataLoader
from transformers import  LlamaForCausalLM, LlamaTokenizer, GenerationConfig, EarlyStoppingCallback
from typing import Union, List
from peft import (LoraConfig, get_peft_model, get_peft_model_state_dict, prepare_model_for_int8_training, set_peft_model_state_dict,)
from few_shot_priming.mylogging import *
from few_shot_priming.config import *
from few_shot_priming.experiments import *
from few_shot_priming.argument_sampling.topic_similarity import *
from few_shot_priming.argument_sampling.diversify import *
from few_shot_priming.prompting_stance import *

def map_two_labels(label):
    label = label.lower()
    if label == "pro":
        return 1
    elif label == "con":
        return 0
    else:
        return random.randint(0,1)

def clean(label):
    if label.lower().startswith("pro"):
        return "pro"
    elif label.lower().startswith("con"):
        return "con"
    elif label.lower().startswith("neutral"):
        return "neutral"
    else:
        return random.choice(["pro", "con", "neutral"])

def map_three_labels(label):
    label = label.lower()
    if label == "pro":
        return 1
    elif label == "con":
        return 0
    else:
        return 2

def generate_prompt(instruction, input=None):
    if input:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
{instruction}
### Input:
{input}
### Response:"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{instruction}
### Response:"""

class Prompter(object):
    __slots__ = ("template", "_verbose")

    def __init__(self, template_name: str = "", verbose: bool = False):
        self._verbose = verbose
        if not template_name:
            # Enforce the default here, so the constructor can be called with '' and will not break.
            template_name = "alpaca"
        file_name = template_name
        if not osp.exists(file_name):
            raise ValueError(f"Can't read {file_name}")
        with open(file_name) as fp:
            self.template = json.load(fp)
        if self._verbose:
            print(
                f"Using prompt template {template_name}: {self.template['description']}"
            )

    def generate_prompt(
            self,
            instruction: str,
            input: Union[None, str] = None,
            label: Union[None, str] = None,
    ) -> str:
        # returns the full prompt from instruction and optional input
        # if a label (=response, =output) is provided, it's also appended.
        if input:
            res = self.template["prompt_input"].format(
                instruction=instruction, input=input
            )
        else:
            res = self.template["prompt_no_input"].format(
                instruction=instruction
            )
        if label:
            res = f"{res}{label}"
        if self._verbose:
            print(res)
        return res

    def get_response(self, output: str) -> str:
        return output.split(self.template["response_split"])[1].strip()

def tokenize(prompt, tokenizer, cutoff_len=256, add_eos_token=True):
    # there's probably a way to do this with the tokenizer settings
    # but again, gotta move fast
    result = tokenizer(
        prompt,
        truncation=True,
        max_length=cutoff_len,
        padding=False,
        return_tensors=None,
    )
    if (
            result["input_ids"][-1] != tokenizer.eos_token_id
            and len(result["input_ids"]) < cutoff_len
            and add_eos_token
    ):
        result["input_ids"].append(tokenizer.eos_token_id)
        result["attention_mask"].append(1)

    result["labels"] = result["input_ids"].copy()

    return result

def generate_instructions(dataset, mapper, examples=None):

    data = {"instruction":[], "input":[], "output":[]}
    label_str = ""
    for i, label in enumerate(mapper):
        if i == 0:
            label_str = mapper[label]
        elif i == len(mapper) - 1:
            label_str = label_str + ", or " +  mapper[label] + "."
        else:
            label_str = label_str + ", " + mapper[label]

    for i, record in dataset.iterrows():
        topic = record["topic"]
        stance = mapper[record["stance"]]
        text = record["text"]
        instruction = f"Classify the stance of the following argument on the given topic into: {label_str}"
        if examples:
            instruction = instruction + examples

        data["instruction"].append(instruction)
        data["output"].append(stance)
        data["input"].append(f"Topic: {topic}\n Argument: {text}")
    return data

def generate_and_tokenize_datasets(data, prompter, tokenizer, cutoff_len, train_on_inputs=True, add_eos_token=False):

    def generate_and_tokenize_prompt(data_point):
        full_prompt = prompter.generate_prompt(
            data_point["instruction"],
            data_point["input"],
            data_point["output"],
        )
        tokenized_full_prompt = tokenize(full_prompt, tokenizer)
        if not train_on_inputs:
            user_prompt = prompter.generate_prompt(
                data_point["instruction"], data_point["input"]
            )
            tokenized_user_prompt = tokenize(
                user_prompt, tokenizer, add_eos_token=add_eos_token, cutoff_len=cutoff_len
            )
            user_prompt_len = len(tokenized_user_prompt["input_ids"])

            if add_eos_token:
                user_prompt_len -= 1

            tokenized_full_prompt["labels"] = [
                                                  -100
                                              ] * user_prompt_len + tokenized_full_prompt["labels"][
                                                                    user_prompt_len:
                                                                    ]  # could be sped up, probably
        return tokenized_full_prompt
    train_data = data["training"].map(generate_and_tokenize_prompt, load_from_cache_file="/tmp/train-data.arrow", num_proc=12)
    val_data = data["validation"].map(generate_and_tokenize_prompt, load_from_cache_file="/tmp/validation-data.arrow", num_proc=12)
    test_data = data["test"].map(generate_and_tokenize_prompt, load_from_cache_file="/tmp/test-data.arrow", num_proc=12)
    return train_data, val_data, test_data

def prepare_dataset(dataset, prompter, label_mapper, tokenizer, logger, cutoff_len, few_shot_size=None, fine_tune=False, diverse=False):
    huggingface_dataset = {}
    #log_message(logger, f'Sampled dataset is {dataset["training"][["topic","stance","id"]].to_string()}')

    #reversed_mapper = {value:key.capitalize() for key,value in label_mapper}
    if not fine_tune:


        examples = format_prompt(dataset["training"], tokenizer, label_mapper,  2048, few_shot_size, logger, alpaca_examples=True)
        log_message(logger, f"foramtting examples {examples}")
    for split in dataset:
        if fine_tune:
            huggingface_dataset[split] = generate_instructions(dataset[split], label_mapper)
        else:
            huggingface_dataset[split] = generate_instructions(dataset[split], label_mapper, examples)
    data = DatasetDict()
    # using your `Dict` object
    for k,v in huggingface_dataset.items():
        data[k] = Dataset.from_dict(v)
    train_data, val_data, test_data = generate_and_tokenize_datasets(data, prompter, tokenizer, cutoff_len=cutoff_len)
    return train_data, val_data, test_data

def train(
        train_data,
        test_data,
        tokenizer,
        model_name,
        logger,
        # model/data params
        base_model: str = "",  # the only required argument

        output_dir: str = "./lora-alpaca",
        # training hyperparams
        batch_size: int = 8,
        micro_batch_size: int = 4,
        num_epochs: int = 30,
        learning_rate: float = 3e-4,
        early_stopping_threshold=0,
        cutoff_len: int = 256,

        val_set_size: int = 0,
        # lora hyperparams
        lora_r: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        lora_target_modules: List[str] = [
            "q_proj",
            "v_proj",
        ],
        # llm hyperparams
        train_on_inputs: bool = True,  # if False, masks out inputs in loss
        add_eos_token: bool = False,
        group_by_length: bool = False,  # faster, but produces an odd training loss curve
        #
        #  params
        resume_from_checkpoint: str = None,  # either training checkpoint or final adapter
        prompt_template_name: str = "alpaca",  # The prompt template to use, will default to alpaca.
):
    if int(os.environ.get("LOCAL_RANK", 0)) == 0:
        print(
            f"Training Alpaca-LoRA model with params:\n"
            f"base_model: {base_model}\n"
            f"output_dir: {output_dir}\n"
            f"batch_size: {batch_size}\n"
            f"micro_batch_size: {micro_batch_size}\n"
            f"num_epochs: {num_epochs}\n"
            f"learning_rate: {learning_rate}\n"
            f"cutoff_len: {cutoff_len}\n"
            f"val_set_size: {val_set_size}\n"
            f"lora_r: {lora_r}\n"
            f"lora_alpha: {lora_alpha}\n"
            f"lora_dropout: {lora_dropout}\n"
            f"lora_target_modules: {lora_target_modules}\n"
            f"train_on_inputs: {train_on_inputs}\n"
            f"add_eos_token: {add_eos_token}\n"
            f"group_by_length: {group_by_length}\n"

            f"resume_from_checkpoint: {resume_from_checkpoint or False}\n"
            f"prompt template: {prompt_template_name}\n"
        )
    gradient_accumulation_steps = batch_size // micro_batch_size

    device_map = "auto"
    world_size = 1
    ddp = world_size != 1
    if ddp:
        device_map = 0
        gradient_accumulation_steps = gradient_accumulation_steps // world_size


    tokenizer.pad_token_id = (0)  # unk. we want this to be different from the eos token
    tokenizer.padding_side = "left"  # Allow batched inference
    model = LlamaForCausalLM.from_pretrained(model_name,  device_map = device_map, torch_dtype=torch.float16, )
    config = LoraConfig(r=lora_r, lora_alpha=lora_alpha, target_modules=lora_target_modules, lora_dropout=lora_dropout, bias="none", task_type="CAUSAL_LM",)


    model = get_peft_model(model, config)
    model.print_trainable_parameters()  # Be more transparent about the % of trainable params.

    if not ddp and torch.cuda.device_count() > 1:
        # keeps Trainer from trying its own DataParallelism when more than 1 gpu is available
        model.is_parallelizable = True
        model.model_parallel = True

    trainer = transformers.Trainer(
        model=model,
        train_dataset=train_data,
        eval_dataset=train_data,
        callbacks = [EarlyStoppingCallback(early_stopping_patience=1, early_stopping_threshold=early_stopping_threshold)],
        args=transformers.TrainingArguments(
            per_device_train_batch_size=micro_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            warmup_steps=100,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            fp16=True,
            logging_steps=10,
            optim="adamw_torch",
            evaluation_strategy="steps",
            save_strategy="steps",
            eval_steps=10 ,
            save_steps=10,
            lr_scheduler_type='linear',
            output_dir=output_dir,
            metric_for_best_model="loss",
            save_total_limit=3,
            load_best_model_at_end=True,
            ddp_find_unused_parameters=False if ddp else None,
            group_by_length=group_by_length,
            run_name="alpaca-ta",
            do_eval=True,
            report_to="none",
        ),
        data_collator=transformers.DataCollatorForSeq2Seq(
            tokenizer, pad_to_multiple_of=8, return_tensors="pt", padding=True
        ),
    )
    model.config.use_cache = False

    old_state_dict = model.state_dict
    model.state_dict = (
        lambda self, *_, **__: get_peft_model_state_dict(
            self, old_state_dict()
        )
    ).__get__(model, type(model))

    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)

    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    #model.save_pretrained(output_dir)
    log = trainer.state.log_history
    df = pd.DataFrame(log)
    columns = ["eval_loss", "train_loss", "epoch", "step"]
    if len(list(df.columns.intersection(columns))) != 4:
        #log_message(logger, df[columns].dropna().to_string())
        df = df[df.columns.intersection(columns)]
    if len(list(df.columns)):
        log_message(logger, df.to_string())
    return model

def evaluate(experiment, model, validate, test_data, tokenizer, logger):

    if validate:
        experiment_type = "validation"
    else:
        experiment_type = "test"

    if experiment == "ibmsc":
        mapper_function = map_two_labels
    else:
        mapper_function = map_three_labels
    test_dataloader = DataLoader(test_data, batch_size=1)
    all_test_preds = []
    all_test_labels = []
    generation_config = GenerationConfig()
    for step, (test_input) in enumerate(test_dataloader):
        #log_message(logger, test_input["instruction"], level=logging.INFO)
        prompt = generate_prompt(test_input["instruction"][0], test_input["input"][0])
        log_message(logger, test_input["instruction"][0], level=logging.INFO)

        inputs = tokenizer(prompt, return_tensors="pt")

        input_ids = inputs["input_ids"].cuda()
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=4
        )

        for s in generation_output.sequences:
            output = tokenizer.decode(s)
            label = output.split("### Response:")[1].strip().lower()
            log_message(logger, f"Prediction {label}", level=logging.INFO)
            log_message(logger, f"Prediction cleaned {clean(label)}", level=logging.INFO)
            all_test_preds.append(clean(label))
        log_message(logger, f"Label {test_input['output']}", level=logging.INFO)
        all_test_labels.append(test_input["output"][0])

    all_test_preds = list(map(mapper_function, all_test_preds))
    all_test_labels = list(map(mapper_function, all_test_labels))
    test_accuracy = accuracy_score(all_test_labels, all_test_preds)
    macro_f1 = f1_score(all_test_labels, all_test_preds, average="macro")
    if experiment == "vast":
        f1s = f1_score(all_test_labels, all_test_preds, average=None, labels=[0, 1, 2])
        metrics = {f"{experiment_type}/accuracy": test_accuracy, f"{experiment_type}/macro-f1":macro_f1, f"{experiment_type}/con-f1":f1s[0], f"{experiment_type}/pro-f1":f1s[1], f"{experiment_type}/neutral-f1":f1s[2]}
    else:
        f1s = f1_score(all_test_labels, all_test_preds,average=None, labels=[0, 1])
        metrics = {f"{experiment_type}/accuracy": test_accuracy, f"{experiment_type}/macro-f1":macro_f1, f"{experiment_type}/con-f1":f1s[0], f"{experiment_type}/pro-f1":f1s[1]}

    return metrics


def run_instructiona_fine_tuning_similar(config, params, experiment, validate, logger, debug=False, topic_count=None, similarity=None, fine_tune=True, analyze_primes=False):
    all_test_preds = []
    all_test_labels = []
    cutoff_len = 2048
    few_shot_size = config["few-shot-size"]

    path_template = get_template_path()
    model_name = config["model-name"]
    tokenizer_name = config["tokenizer-name"]
    prompter = Prompter(path_template)
    tokenizer = LlamaTokenizer.from_pretrained(tokenizer_name)
    dataset = load_splits(experiment, oversample=False, topic_count=topic_count, debug=debug)
    if topic_count:
        log_message(logger, f"training on {topic_count} topics")
        log_message(logger, f"loaded {len(dataset['training'])} arguments in the training set")
    if validate:
        experiment_type = "validation"
    else:
        experiment_type = "test"

    if experiment == "ibmsc":
        mapping_dictionary = {0: "Con", 1: "Pro"}
        mapper_function = map_two_labels
    else:
        mapping_dictionary = {0: "Con", 1: "Pro", 2: "Neutral"}
        mapper_function = map_three_labels

    test_dataloader = DataLoader(dataset[experiment_type], batch_size=1)
    generation_config = GenerationConfig()

    similarities = load_similarities(experiment, experiment_type, similarity)
    new_dataset = {}
    prime_analysis_dataset =[]
    if fine_tune:
        train_data, val_data, test_data = prepare_dataset(dataset, prompter, mapping_dictionary, tokenizer, logger, cutoff_len, few_shot_size=config["few-shot-size"], fine_tune=fine_tune)
        if validate:
            test_data = val_data
    test_index = 0

    for _, record in dataset[experiment_type].iterrows():
        log_message(logger, f"sampling few shots for {record['text']}", level=logging.INFO)
        few_shots, scores = sample_similar_examples(record["id"], similarities, dataset["training"], few_shot_size)
        log_message(logger, f"most similar is {few_shots.iloc[0]['text']}", level=logging.INFO)
        new_dataset["training"] = few_shots
        if fine_tune:
            new_dataset["test"] = pd.DataFrame({})
            new_dataset["validation"] = pd.DataFrame({})
            train_data, _, _ = prepare_dataset(new_dataset, prompter, mapping_dictionary, tokenizer, logger, cutoff_len, few_shot_size=config["few-shot-size"], fine_tune=fine_tune)
        else:
            new_dataset["test"] = dataset["test"]
            new_dataset["validation"] = dataset["validation"]
            train_data, val_data, test_data = prepare_dataset(new_dataset, prompter, mapping_dictionary, tokenizer, logger, cutoff_len, few_shot_size=config["few-shot-size"], fine_tune=fine_tune)
            if validate:
                test_data = val_data

        log_message(logger,f"++ training  with few shot size {few_shot_size} ++")
        if fine_tune:
            model = train(train_data, test_data, tokenizer, model_name, logger, batch_size=params["batch-size"], num_epochs=params["epochs"],
                          learning_rate= params["learning-rate"], early_stopping_threshold=params["early-stopping-threshold"],
                          output_dir=config["model-path-fine-tuned"])
        else:
            model = LlamaForCausalLM.from_pretrained(model_name,  device_map = "auto", torch_dtype=torch.float16, )
        test_input = test_data[test_index]
        prompt = generate_prompt(test_input["instruction"], test_input["input"])
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].cuda()

        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=4
        )

        log_message(logger,"++ evaluation ++")
        for s in generation_output.sequences:
            output = tokenizer.decode(s)
            label = output.split("### Response:")[1].strip().lower()

            log_message(logger, f"Prediction {label}", level=logging.INFO)
            label = clean(label.lower())
            log_message(logger, f"Prediction cleaned {label}", level=logging.INFO)
        all_test_preds.append(label)
        all_test_labels.append(test_input["output"].lower())
        log_message(logger, f"Label {test_input['output'].lower()}", level=logging.INFO)

        #all_test_labels.append(record["stance"])
        test_index = test_index + 1
        if analyze_primes:
            few_shots["test-claim-id"] = record["id"]
            few_shots["test-claim"] = record["text"]
            few_shots["test-topic"] = record["topic"]
            few_shots["test-stance"] = record["stance"]
            few_shots["test-stance-from-hf-dataset"] = test_input["output"]
            few_shots["test-predicted-stance"] = (1 if "pro" == label else 0)
            prime_analysis_dataset.append(few_shots)

    all_test_preds = list(map(mapper_function, all_test_preds))
    all_test_labels = list(map(mapper_function, all_test_labels))
    test_accuracy = accuracy_score(all_test_labels, all_test_preds)
    macro_f1 = f1_score(all_test_labels, all_test_preds, average="macro")
    if experiment=="vast":
        f1s = f1_score(all_test_labels, all_test_preds, average=None, labels=[0, 1, 2])
        metrics = {f"{experiment_type}/accuracy": test_accuracy, f"{experiment_type}/macro-f1":macro_f1, f"{experiment_type}/con-f1":f1s[0], f"{experiment_type}/pro-f1":f1s[1], f"{experiment_type}/neutral-f1":f1s[2]}
    else:
        f1s = f1_score(all_test_labels, all_test_preds,average=None, labels=[0, 1])
        metrics = {f"{experiment_type}/accuracy": test_accuracy, f"{experiment_type}/macro-f1":macro_f1, f"{experiment_type}/con-f1":f1s[0], f"{experiment_type}/pro-f1":f1s[1]}
    if analyze_primes:
        pd_prime_anaylsis = pd.concat(prime_analysis_dataset)
        pd_prime_anaylsis.to_csv("/bigwork/nhwpajjy/few-shot-priming/results/prime-analysis.tsv", sep="\t")
    log_metrics(logger, metrics, level=logging.WARNING)
    return metrics


def run_instructional_fine_tuning(config, params, experiment, validate, logger, debug, topic_count=None, sampling_strategy=None, similarity=None, fine_tune=True, analyze_primes=False):

    if sampling_strategy =="similar":
        return run_instructiona_fine_tuning_similar(config, params, experiment, validate, logger, debug, topic_count, similarity, fine_tune=fine_tune, analyze_primes=analyze_primes)
    else:
        cutoff_len= 2048
        path_template = get_template_path()
        model_name = config["model-name"]
        tokenizer_name = config["tokenizer-name"]
        prompter = Prompter(path_template)
        tokenizer = LlamaTokenizer.from_pretrained(tokenizer_name)
        if topic_count:
            log_message(logger, f"training on {topic_count} topics")
        dataset = load_splits(experiment, oversample=True, topic_count=topic_count, debug=debug)
        log_message(logger, f"dataset loaded with {len(dataset['training'])} instances in the training dataset", level=logging.WARNING)

        if experiment == "ibmsc":
            mapping_dictionary = {0: "Con", 1: "Pro"}
        else:
            mapping_dictionary = {0: "Con", 1: "Pro", 2: "Neutral"}

        if validate:
            experiment_type = "validation"
        else:
            experiment_type = "test"
        diverse = False
        if sampling_strategy == "diverse":
            diverse = True

            few_shots = sample_diverse_examples(experiment, experiment_type, config["few-shot-size"], logger, topic_count=topic_count)
            if topic_count:
                log_message(logger, f"training on {topic_count} topics")
                log_message(logger, f"loaded {len(few_shots)} arguments in the training set")

            log_message(logger, f"sampling diverse few shots got {len(few_shots)}")
            log_message(logger, f"diverse few shots are {few_shots[['topic','stance','id']].to_string()}")
            dataset["training"] = few_shots
        else:
            dataset["training"] = dataset["training"].sample(config["few-shot-size"])
        dataset["training"].sort_values("topic", inplace=True)
        train_data, val_data, test_data = prepare_dataset(dataset, prompter, mapping_dictionary, tokenizer, logger, cutoff_len=cutoff_len,
                                                          few_shot_size=config["few-shot-size"], fine_tune=fine_tune, diverse=diverse, )
        log_message(logger, tokenizer.decode(train_data[0]["input_ids"]))
        if validate:
            test_data = val_data
        log_message(logger,"** training ++")
        if fine_tune:
            model = train(train_data, test_data, tokenizer, model_name, logger, batch_size=params["batch-size"],
                          num_epochs=params["epochs"], output_dir=config["model-path-fine-tuned"], learning_rate= params["learning-rate"],
                          early_stopping_threshold=params["early-stopping-threshold"], cutoff_len=cutoff_len)
        else:
            model = LlamaForCausalLM.from_pretrained(model_name,  device_map = "auto", torch_dtype=torch.float16, )
        #model = None
        log_message(logger,"** evaluating ++")
        metrics = evaluate(experiment, model, validate, test_data, tokenizer, logger)
        log_metrics(logger, metrics, level=logging.WARNING)
        return metrics



