from random import random
from flask import Blueprint, request, jsonify
import pandas as pd

bp = Blueprint("index", __name__)

model = pd.read_csv("symbols.csv", index_col="symbol")


@bp.route("/generate", methods=["GET"])
def generate_new():
    def create_articulation_dict(label, phoneme_dict, phonemes):
        for k, v in phoneme_dict.items():
            if k not in phonemes:
                phonemes[k] = {}
            phonemes[k][label] = v

    def get_phonemes_with_voicing_contrast(condition_label, condition_value, features):
        if features["voicing_contrast"] == "both":
            return model[model[condition_label] == condition_value]
        elif features["voicing_contrast"] == "none":
            return model[(model[condition_label] == condition_value) & (model["vce"] == "-")]
        elif features["voicing_contrast"] == "plosives":
            return pd.concat(
                [
                    model[(model[condition_label] == condition_value) & (model["cnt"] == "-")],
                    model[(model[condition_label] == condition_value) & (model["cnt"] == "+") & (model["vce"] == "-")],
                ]
            )
        elif features["voicing_contrast"] == "fricatives":
            return pd.concat(
                [
                    model[(model[condition_label] == condition_value) & (model["cnt"] == "+")],
                    model[(model[condition_label] == condition_value) & (model["cnt"] == "-") & (model["vce"] == "-")],
                ]
            )

    phonemes = {}

    # come up with some general features of the phoneme inventory here
    features = {}
    r = random()
    # voicing contrast (numbers taken from WALS)
    if r < 0.32:
        features["voicing_contrast"] = "none"
    elif r < 0.65:
        features["voicing_contrast"] = "plosives"
    elif r < 0.72:
        features["voicing_contrast"] = "fricatives"
    else:
        features["voicing_contrast"] = "both"

    r = random()
    if r < 0.895:
        features["missing_consonants"] = "none"
    elif r < 0.98:
        features["missing_consonants"] = "fricatives"
    elif r < 0.998:
        features["missing_consonants"] = "nasals"
    else:
        features["missing_consonants"] = "fricatives_and_nasals"

    if random() < 0.98:
        # add labials
        # get rows from model with +lab
        # add the symbol to phonemes list
        labials = get_phonemes_with_voicing_contrast("lab", "+", features)

        for column_name, phoneme in labials.items():
            # print(column_name, phoneme.to_dict())
            create_articulation_dict(column_name, phoneme.to_dict(), phonemes)
    # generate alveolars (make this choose between dentals and alveolars, or both?)
    r = random()
    coronals = None
    if r < 0.45:
        coronals = get_phonemes_with_voicing_contrast("cor", 2, features)
    elif r < 0.9:
        coronals = get_phonemes_with_voicing_contrast("cor", 1, features)
    else:
        coronals = pd.concat(
            [
                get_phonemes_with_voicing_contrast("cor", 2, features),
                get_phonemes_with_voicing_contrast("cor", 1, features),
            ]
        )
    for column_name, phoneme in coronals.items():
        create_articulation_dict(column_name, phoneme.to_dict(), phonemes)

    return jsonify(phonemes)
