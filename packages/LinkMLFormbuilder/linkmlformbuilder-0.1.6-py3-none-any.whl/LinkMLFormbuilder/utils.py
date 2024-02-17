import re

HTML_START = '''<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>LinkML JSON schema form builder</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
</head>
<style>
'''
HTML_START_PART2 = '''
</style>
<body>
'''
HTML_START_HTML_ONLY = '''<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>LinkML JSON schema form builder</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
</head>
<style>
    .form-text {
        font-style: italic;
        width: -webkit-fill-available;
    }

    p :not(.form-description){
        margin-bottom: 0px !important;
    }

    .form-description {
        margin-top: 0px !important;
        margin-bottom: 20px;
    }

    body {
        margin-left: 10px !important;
    }

    label {
        font-weight: normal !important;
    }

    .input-group {
        width: -webkit-fill-available !important;
        display: table !important;
    }

    .mb-3 {
        margin-bottom: 1rem !important;
    }

    .input-group-text {
        padding: .5rem .75rem;
        font-weight: 400;
        line-height: 1.5;
        color: #212529;
        text-align: center;
        white-space: nowrap;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        width: 20%;
        float: left;
        min-height: 34px;
        white-space: pre-wrap;
    }

    .form-control {
        width: 80% !important;
        height: 100%;
    }

    .input-group {
        position: relative;
        display: flex;
        flex-wrap: wrap;
        align-items: stretch;
        width: 100%;
    }

    .hidden {
        visibility: hidden;
    }

    .form-check {
        width: fit-content;
        display: inline-block;
        margin-right: 5px;
    }

    .values-from {
        font-weight: bold;
        margin-right: 5px;
    }

    .values-from-dynamic {
        font-weight: bold;
        margin-right: 5px;
        float: left;
        width: calc(20% - 5px);
    }

    h2 {
        width: 100vw;
    }
</style>
<body>
'''
HTML_END = '''</body>
</html>'''

SEPARATOR = " / "
ALIASES = "aliases"
STRUCTURED_ALIASES = "structured_aliases"
LOCAL_NAMES = "local_names"
TITLE = "title"
DESCRIPTION = "description"
ALT_DESCRIPTIONS = "alt_descriptions"
MULTIVALUED = "multivalued"
MAXIMUM_CARDINALITY = "maximum_cardinality"
SINGULAR_NAME = "singular_name"

def extractAliases(sourceCode):
    name = ""
    if (ALIASES in sourceCode or STRUCTURED_ALIASES in sourceCode or LOCAL_NAMES in sourceCode):
        name += " ("
        if (ALIASES in sourceCode):
            for alias in sourceCode.get(ALIASES):
                name += alias + SEPARATOR
        if (STRUCTURED_ALIASES in sourceCode):
            structured_aliases = sourceCode.get(STRUCTURED_ALIASES)
            for structured_alias in structured_aliases:
                if (TITLE in structured_alias):
                    name += structured_alias.get(TITLE) + SEPARATOR
                else:
                    name += structured_alias.get("literal_form") + SEPARATOR
        if (LOCAL_NAMES in sourceCode):
            for local_name in sourceCode.get(LOCAL_NAMES):
                name += local_name.get("local_name_value") + SEPARATOR
        name = name[:-3] + ")"
    return name

def extractName(classCode):
    return (classCode.get(TITLE) if (TITLE in classCode) else classCode.get("name")) + extractAliases(classCode)

def extractDescription(itemCode):
    description = ""
    if (DESCRIPTION in itemCode):
        description = normalize_description(itemCode.get(DESCRIPTION))
    if (ALT_DESCRIPTIONS in itemCode):
        description += " ("
        for alt_description in itemCode.get(ALT_DESCRIPTIONS):
            description += normalize_description(alt_description.get(DESCRIPTION)) + SEPARATOR
        description = description[:-3] + ")"
    return description

def extractSlotName(slotCode):
    name = ""
    if (((MULTIVALUED in slotCode and slotCode.get(MULTIVALUED) == False) or (MAXIMUM_CARDINALITY in slotCode and slotCode.get(MAXIMUM_CARDINALITY) == 1)) and SINGULAR_NAME in slotCode):
        name = slotCode.get(SINGULAR_NAME) # cardinality is either 0..1 or 1..1
    else:
        name += extractName(slotCode)
    return name

def normalize_description(desc): # remove html tags <p><div>, remove anything in <i> and <img>
    p = re.compile(r'<.*?>')
    return p.sub('', desc).strip()

def capitalizeLabel(label):
    if (len(label) == 0): return label
    return label[0].upper() + label[1:]
