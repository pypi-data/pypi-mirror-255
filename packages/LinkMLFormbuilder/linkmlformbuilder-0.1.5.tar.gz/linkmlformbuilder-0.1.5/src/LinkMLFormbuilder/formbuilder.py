import argparse
import yaml
from LinkMLFormbuilder import utils
import os
import pdfkit
from LinkMLFormbuilder import slot_code_generators
from shutil import which
import pkg_resources
# import slot_code_generators
# import utils

def retrieveFileContent(yamlfile):
    try:
        stream = open(os.path.abspath(yamlfile), "r")
        return yaml.safe_load(stream)
    except yaml.YAMLError:
        print("File could not be parsed")
        exit(1)
    except Exception:
        print("Could not retrieve file content, please make sure the path is correct")
        exit(1)

def getSlotFormCode(slotCode, content, default_range, subclasses, level):
    desc = utils.extractDescription(slotCode)
    required = "required" if ("required" in slotCode and slotCode.get("required") == True) else ""
    propertyName = slotCode.get("name")
    title = utils.extractSlotName(slotCode)
    
    if ("values_from" in slotCode or ("range" in slotCode and slotCode.get("range") in content.get("enums"))):
        return slot_code_generators.getEnumSlotCode(slotCode, content, desc, required, propertyName, title)
    elif ("enum_range" in slotCode): # inlined enum
        return slot_code_generators.getInlineEnumSlotCode(slotCode, desc, required, propertyName, title)
    elif ("range" in slotCode):
        if (slotCode.get("range") in content.get("classes")):
            return getClassFormCode(content.get("classes").get(slotCode.get("range")), content, default_range, subclasses, level + 1) # the range is a class itself and should be treated as such
        elif (slotCode.get("range") == "integer" or slotCode.get("range") == "float"):
            return slot_code_generators.getNumberSlotCode(slotCode, desc, required, propertyName, title)
        elif (slotCode.get("range") == "string"): #assume textarea
            return slot_code_generators.getTextareaSlotCode(desc, required, propertyName, title)
        elif (slotCode.get("range") == "boolean"):
            return slot_code_generators.getBooleanSlotCode(desc, required, propertyName, title)
        else: # this is a basic pdf, so datetime should not be a datetime field, but a textfield
            return slot_code_generators.getStringSlotCode(desc, required, propertyName, title)
    else: # rely on default range
        if (default_range is not None):
            if (default_range == "integer" or default_range == "float"):
                return slot_code_generators.getNumberSlotCode(slotCode, desc, required, propertyName, title)
            elif (default_range == "string"): #assume textarea
                return slot_code_generators.getTextareaSlotCode(desc, required, propertyName, title)
            elif (default_range == "boolean"):
                return slot_code_generators.getBooleanSlotCode(desc, required, propertyName, title)
            else: # this is a basic pdf, so datetime should not be a datetime field, but a textfield
                return slot_code_generators.getStringSlotCode(desc, required, propertyName, title)
        else:
            raise Exception("Invalid LinkML. There should either be a explicitly defined range for slot {slot}, or a default_range.".format(slot=slotCode.get("name")))

def getClassFormCode(classCode, content, default_range, subclasses, level):
    title = utils.extractName(classCode)
    code = '''<h{level}>{title}</h{level}>\n'''.format(level = level + 1, title = title)
    code += "<p class='form-description'>Form description: " + utils.capitalizeLabel(utils.extractDescription(classCode)) + "</p>\n"
    if ("is_a" in classCode): # process superclass first
        superClassName = classCode.get("is_a")
        superClassCode = content.get("classes").get(superClassName)
        for slot in superClassCode.get("slots"):
            if (slot not in classCode.get("slot_usage")): # this slot is not further specified in the class itself
                slotCode = content.get("slots").get(slot)
                code += getSlotFormCode(slotCode, content, default_range, subclasses, level)
    if ("mixins" in classCode): # then process mixins
        for key in classCode.get("mixins"):
            mixinCode = content.get("classes").get(key)
            for slot in mixinCode.get("slots"):
                if (slot not in classCode.get("slot_usage")): # this slot is not further specified in the class itself
                    slotCode = content.get("slots").get(slot)
                    code += getSlotFormCode(slotCode, content, default_range, subclasses, level)
    
    gen = (slot for slot in classCode.get("slots") if content.get("slots").get(slot).get("range") not in subclasses)
    gen2 = (slot for slot in classCode.get("slots") if content.get("slots").get(slot).get("range") in subclasses)
    if ("slots" in classCode):
        for slot in gen: #process slots of this class
            slotCode = content.get("slots").get(slot)
            code += getSlotFormCode(slotCode, content, default_range, subclasses, level)
    if ("attributes" in classCode): #inline slots
        for slot in classCode.get("attributes"):
            slotCode = classCode.get("attributes").get(slot)
            code += getSlotFormCode(slotCode, content, default_range, subclasses, level)
    if ("slots" in classCode):
        for slot in gen2: #process slots of this class where the range is a subclass
            slotCode = content.get("slots").get(slot)
            code += getSlotFormCode(slotCode, content, default_range, subclasses, level)
    return code


def buildForm(content, html_only, output_directory, name, testEnv = False):
    NAME = name if (name != "default") else content.get("name")
    OUTPUT_DIR = os.getcwd() if (output_directory == "cwd") else os.path.abspath(output_directory)
    HTML_PATH = os.path.join(OUTPUT_DIR, NAME + ".html")
    f = open(HTML_PATH, "x", encoding="utf-8")
    if (html_only == True):
        f.write(utils.HTML_START_HTML_ONLY)
    else:
        f.write(utils.HTML_START)
        f.write(pkg_resources.resource_string(__name__, "bootstrap.css").decode('utf-8'))
        f.write("\n")
        f.write(pkg_resources.resource_string(__name__, "styles.css").decode('utf-8'))
        f.write(utils.HTML_START_PART2)
    title = utils.extractName(content)
    f.write("<h1>" + title + "</h1>\n")
    default_range = content.get("default_range") if ("default_range" in content) else None
    classes = []
    superClasses = []
    subClasses = [] # all classes that are technically containers/subclasses
    for key in content.get("slots"):
        slotCode = content.get("slots").get(key)
        if (slotCode.get("range") in content.get("classes")):
            subClasses.append(slotCode.get("range"))

    for key in content.get("classes"):
        classCode = content.get("classes").get(key)       
        if ("is_a" in classCode):
            superClasses.append(classCode.get("is_a"))
        if ("mixin" in classCode and classCode.get("mixin") == True): # it is a mixin
            superClasses.append(key)
        if ("mixins" in classCode): # it inherits from other classes which should not be shown separately in forms
            for key in classCode.get("mixins"):
                superClasses.append(key)
        
        if (key not in superClasses and key not in subClasses):
            classes.append(key)
    for key in classes:
        classCode = content.get("classes").get(key)
        if ("abstract" not in classCode or classCode.get("abstract") == False): # if the class is abstract, it should not be in the form
            f.write(getClassFormCode(classCode, content, default_range, subClasses, 1))
    f.write(utils.HTML_END)
    f.close()
    if (not html_only):
        options = { 
        'margin-bottom': '1cm', 
        'footer-right': '[page] of [topage]',
        }
        pdfkit.from_file(HTML_PATH, os.path.join(OUTPUT_DIR, NAME + ".pdf"), options=options)
    if (testEnv):
        f = open(HTML_PATH, "r", encoding="utf-8")
        html_result = f.read()
        f.close()
        return html_result

def cli():
    if (which("wkhtmltopdf") is None):
        #install somehow, for now: error
        os.error("wkhtmltopdf is not installed, please install from: https://wkhtmltopdf.org/downloads.html")
        exit(1)
    
    parser = argparse.ArgumentParser("linkmlformbuilder")
    parser.add_argument("yamlfile", help="The LinkML yaml file for which a form should be built")
    parser.add_argument("-html", "--html_only", dest="html_only", action="store_true", help="This flag is used when the user only wants an HTML file returned, there will be no PDF export", default=False)
    parser.add_argument("-dir", "--output_directory", dest="output_directory", help="Specify an output directory, the current working directory is used when this value not provided or the flag is missing", nargs="?", default="cwd", const="cwd")
    parser.add_argument("--name", help="Specify an alternative file name, do not specify a file extension. By default, the filename of the yamlfile is used for the HTML and optionally PDF files", nargs="?", default="default", const="default")
    args = parser.parse_args()
    buildForm(retrieveFileContent(args.yamlfile), args.html_only, args.output_directory, args.name)

if __name__ == "__main__":
    cli()
