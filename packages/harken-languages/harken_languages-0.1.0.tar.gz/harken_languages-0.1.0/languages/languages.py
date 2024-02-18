import json

from langcodes import Language, tag_is_valid, standardize_tag
from polyglot.detect import Detector

from lingua import Language, LanguageDetectorBuilder

detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

ISO_639_1 = '639-1'
ISO_639_2 = '639-2'

import warnings
from iso639 import Lang

warnings.filterwarnings("ignore")

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

DEEPL_LANGUAGES = json.load(open(os.path.join(dir_path,"data/deepl_languages.json"),"r"))
GOOGLE_LANGUAGES = json.load(open(os.path.join(dir_path,"data/google_languages.json"),"r"))
GENERAL_LANGUAGES = json.load(open(os.path.join(dir_path,"data/general_languages.json"),"r"))


def get_language_from_dict(lang):
    try:
        lang = GENERAL_LANGUAGES[lang]
    except:
        lang = get_language_code(lang)
    return lang


def language_detector_polyglot(text):
    result = Detector(text + " " + text + " " + text)
    results = []
    for language in result.languages:
        lang = get_language_info(language.code)
        lang["score"] = language.confidence / 100
        results.append(lang)
    return results


def language_detector_lingua(text):
    confidence_values = detector.compute_language_confidence_values(text + " " + text + " " + text)
    results = []
    for lang, score in confidence_values:
        lang = get_language_info(lang)
        lang["score"] = score
        results.append(lang)
    return results


def detect_possible_languages(text, k=3, detector="polyglot"):
    try:
        if detector == "polyglot":
            results = language_detector_polyglot(text=text)
        elif detector == "lingua":
            results = language_detector_lingua(text=text)
        return results[0:k]
    except:
        return [{'name': 'Unknown', 'code': 'unk', 'display': 'Unknown', 'code3': 'unk', 'score': 0}]


def detect_language(text, detector="polyglot"):
    try:
        if detector == "polyglot":
            results = language_detector_polyglot(text=text)
        elif detector == "lingua":
            results = language_detector_lingua(text=text)
        return results[0]
    except:
        return {'name': 'Unknown', 'code': 'unk', 'display': 'Unknown', 'code3': 'unk', 'score': 0}


def detect_language_code(text, iso=ISO_639_1, detector="polyglot"):
    language = detect_language(text, detector=detector)
    return get_language_code(language=language['lang'], iso=iso)


def get_language_info(language):
    try:
        obj = Lang(language)
        return {'name': obj.name, 'code': obj.pt1, 'display': obj.name, 'code3': obj.pt3}
    except:
        pass
    try:
        obj = Language.get(language)
        return {'name': obj.language_name(), 'code': standardize_tag(obj.to_alpha3()), 'display': obj.display_name(),
                'code3': obj.to_alpha3()}
    except:
        return {'name': 'Unknown', 'code': 'unk', 'display': 'Unknown', 'code3': 'unk'}


def get_language_code(language, iso=ISO_639_1):
    return get_language_info(language)['code' if iso == ISO_639_1 else 'code3']


def is_a_valid_language(language):
    return tag_is_valid(language)


__all__ = ["detect_language", "detect_language_code", "is_a_valid_language", "detect_possible_languages",
           "get_language_from_dict", "get_language_info", "get_language_code", "ISO_639_1", "ISO_639_2",
           "DEEPL_LANGUAGES", "GOOGLE_LANGUAGES", "GENERAL_LANGUAGES"]
