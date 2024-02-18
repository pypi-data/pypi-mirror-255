from log_analyzer_cwj import logAnalyzer
from log_analyzer_cwj import innerRule


def start(_ruleFile, _fastMode, _multilineTime, _blankLine):
    print('------------start---------------')
    return logAnalyzer.log_analyze(_ruleFile, _fastMode, _multilineTime, _blankLine)


def json_all_to_dict(jsonString):
    return logAnalyzer.json_all_to_dict(jsonString)


def dict_value_in_list(list, dictKey, start = 0, index = -1):
    return innerRule.dict_value_in_list(list, dictKey, start, index)


def prepare_sequence(eventDict, startFlag):
    return innerRule.prepare_sequence(eventDict, startFlag)


def prepare_single(eventDict):
    return innerRule.prepare_single(eventDict)