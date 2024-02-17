import pandas as pd
import os
from few_shot_priming.config import *
from few_shot_priming.argument_sampling.topic_similarity import *

def save_splits():
    """
    Save the splits of the experiments by sampling a validation set from the training set with exclusive topic sets
    :return:
    """
    path_source, path_training, path_validation, path_test = get_experiment_paths()
    df_arguments = pd.read_csv(path_source, sep=",", encoding="utf-8")
    df_training = df_arguments[df_arguments["split"] == "train"]
    df_test = df_arguments[df_arguments["split"] == "test"]
    training_topics = df_training["topicTarget"].sample(12).unique()
    training_topics = training_topics[:10]
    df_sampled_training = df_training[df_training["topicTarget"].isin(training_topics)]
    df_validation = df_training[~df_training["topicTarget"].isin(training_topics)]
    df_sampled_training.to_csv(path_training, sep=",", encoding="utf-8", index=False)
    df_validation.to_csv(path_validation, sep=",", encoding="utf-8", index=False)
    df_test.to_csv(path_test, sep=",", encoding="utf-8", index=False)


def oversample_dataset(df, experiment):
    if experiment == "ibmsc":
        pro_claims = df[df["claims.stance"]=="Pro"]
        con_claims = df[df["claims.stance"]=="Con"]
        count_of_con_to_sample = pro_claims.shape[0] - con_claims.shape[0]
        if count_of_con_to_sample > 0:
            if count_of_con_to_sample <= len(con_claims):
                con_claims_to_add = con_claims.sample(count_of_con_to_sample)
            else:
                con_claims_to_add = con_claims.sample(count_of_con_to_sample, replace=True)
            df = pd.concat([df, con_claims_to_add])
        elif count_of_con_to_sample < 0:
            count_of_pro_to_sample = - count_of_con_to_sample
            if count_of_pro_to_sample <= len(pro_claims):
                pro_claims_to_add = pro_claims.sample(count_of_pro_to_sample)
            else:
                pro_claims_to_add = pro_claims.sample(count_of_pro_to_sample, replace=True)
            df = pd.concat([df, pro_claims_to_add])
        else:
            pass
        return df
    else:
        max_label_count = df["label"].value_counts().max()
        all_labels_to_add = []
        for label, df_label in df.groupby("label"):
            instances_to_sample = max_label_count -  len(df_label)
            if instances_to_sample <= len(df_label):
                df_label_to_add = df_label.sample(instances_to_sample)
            else:
                df_label_to_add = df_label.sample(instances_to_sample, replace=True)
            all_labels_to_add.append(df_label_to_add)
        all_labels_to_add.append(df)
        return pd.concat(all_labels_to_add)

def adapt_ibmsc(df):
    labels = {"PRO": 1, "CON":0}
    df["stance"] = df["claims.stance"].apply(lambda x: labels[x])
    df = df [["topicText", "claims.claimCorrectedText", "stance", "claims.claimId"]]
    df.rename(columns={"topicText" : "topic", "claims.claimCorrectedText": "text", "claims.claimId": "id"}, inplace=True)
    return df[["topic", "stance", "text", "id"]]

def adapt_vast(df):
    df = df [["topic_str", "post", "label", "new_id"]]
    df.rename(columns={"topic_str":"topic", "post": "text", "label": "stance", "new_id":"id"}, inplace=True)
    #df["topic"] = df["topic"].apply(lambda topic: " ".join(topic))
    #df["stance"] = df["stance"].apply(lambda stance: stance.caplitalize())
    return df[["topic", "stance", "text", "id"]]

def load_splits(experiment, oversample=True, validate=True, best_split=False, adapt=True, topic_count=None, debug=False):
    """
    Load the splits of the experiments and return it in a dictionary of pandas dataframes
    :return: a dictionary containing the training, validation, and test splits
    """
    if experiment == "ibmsc":
        dataset_id="claims.claimId"
        topic_label = "topicText"
    else:
        dataset_id = "new_id"
        topic_label = "topic_str"

    path_source, path_training, path_validation, path_test = get_experiment_paths(experiment)
    if experiment == "ibmsc" and not os.path.exists(path_validation):
        save_splits()
    df_training = pd.read_csv(path_training, sep=",", encoding="utf-8")
    df_validation = pd.read_csv(path_validation, sep=",", encoding="utf-8")
    df_test = pd.read_csv(path_test, sep=",", encoding="utf-8")
    if experiment =="vast":
        df_validation = df_validation[df_validation["seen?"]==0]
        df_test = df_test[df_test["seen?"]==0]
    if debug:
        #df_training = df_training.sample(100)
        df_validation = df_validation.sample(200)
        df_test = df_test.sample(200)

    if not validate:
        df_training = pd.concat([df_training, df_validation])
    if topic_count:
        topics = df_training[topic_label].unique()
        chosen_topics = np.random.choice(topics, topic_count)
        df_training = df_training[df_training[topic_label].isin(chosen_topics)]
    dataset = {"training": df_training, "validation": df_validation, "test": df_test}

    if best_split:
        df_trianing = dataset["training"]
        print(df_trianing["best-split"].value_counts())
        df_trianing["best-split"] = df_trianing["best-split"].astype(bool)
        df_training = df_trianing[df_trianing["best-split"]]
        dataset["training"] = df_training

    elif oversample:
        dataset["training"] = oversample_dataset(dataset["training"], experiment)
    else:
        pass
    for split in dataset:
        dataset[split].sort_values(by=dataset_id, inplace=True)
    if adapt:
        for split in dataset:
            if experiment == "ibmsc":
                dataset[split] = adapt_ibmsc(dataset[split])
            else:
                dataset[split] = adapt_vast(dataset[split])

    return dataset


