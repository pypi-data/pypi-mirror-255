from langchain_openai import ChatOpenAI
from ara_tools.classifier import Classifier
from os.path import exists, join, splitext, isfile
from os import makedirs, listdir, environ
from sys import exit
from subprocess import run
from re import findall

class ChatOpenAISingleton:
    _instance = None

    def __init__(self):
        ChatOpenAISingleton._instance = ChatOpenAI(openai_api_key=environ.get("GPT_KEY"))

    @staticmethod
    def get_instance():
        if ChatOpenAISingleton._instance is None:
            ChatOpenAISingleton()
        return ChatOpenAISingleton._instance    

def write_string_to_file(filename, string, mode):
    with open(filename, mode) as file:
            file.write(f"\n{string}\n")
    return file

def read_string_from_file(path):
    with open(path, 'r') as file:
            text = file.read()
    return text

def read_prompt(classifier, param):
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_path = f"ara/{sub_directory}/{param}.data/prompt.data/{classifier}.prompt"

    prompt = read_string_from_file(prompt_path)
    return prompt

def send_prompt(prompt):
    chat = ChatOpenAISingleton.get_instance()
    chat_result = chat.invoke(prompt)
    return chat_result.content

def append_headings(classifier, param, heading_name):
    sub_directory = Classifier.get_sub_directory(classifier)

    artefact_data_path = f"ara/{sub_directory}/{param}.data/{classifier}_exploration.md"
    content = read_string_from_file(artefact_data_path)
    pattern = r'## {}_(\d+)'.format(heading_name)
    matches = findall(pattern, content)

    max_number = 1
    if matches:
        max_number = max(map(int, matches)) + 1
    heading = f"## {heading_name}_{max_number}"
            
    write_string_to_file(artefact_data_path, heading, 'a')

def write_prompt_result(classifier, param, text):
    sub_directory = Classifier.get_sub_directory(classifier)

    artefact_data_path = f"ara/{sub_directory}/{param}.data/{classifier}_exploration.md"
    write_string_to_file(artefact_data_path, text, 'a')


def prompt_creation(classifier, parameter):
    sub_directory = Classifier.get_sub_directory(classifier)
    
    artefact_path = join(f"ara/{sub_directory}/{parameter}.data")
    if not exists(artefact_path):
        print(f"ERROR: {classifier} {parameter} in does not exist.")
        exit(1)

    prompt_data_path = f"ara/{sub_directory}/{parameter}.data/prompt.data"
    makedirs(prompt_data_path, exist_ok=True)
    ensure_basic_prompt_files_exists(classifier, prompt_data_path)
    create_prompt(classifier, prompt_data_path)

def ensure_basic_prompt_files_exists(classifier, prompt_data_path):
    """
    Ensures that all basic prompt files for a given classifier exist within the specified directory and creates them if they don't.
    
    :param classifier: The type of artefact (e.g., 'feature', 'vision'), which determines the template used for file creation.
    :param prompt_data_path: The path to the directory where 'prompt.data' files are stored.
    :return: Returns 'False' if any file was created during the execution, indicating that the user should review these files.
             Returns 'True' if all files were already in place.

    Note: 
    - The function prints a message listing the newly created files, if any.
    - The content for 'prompt.md' and 'givens.md' requires further manual editing.
    """
    basic_prompt_files = ["commands.md", "givens.md", "prompt.md", "rules.md"]
    basic_prompt_files = set(filter(lambda file: need_to_be_created(file, prompt_data_path), basic_prompt_files))
    
    for basic_file in basic_prompt_files:
        file_path = join(prompt_data_path, basic_file)
        with open(file_path, 'w') as file:
            content = basic_prompt_file_content_creation(classifier, basic_file)
            file.write(content)

    if basic_prompt_files:
        print(f"Following File(s) were created: {basic_prompt_files}. \nCheck these files and continue by re-entering the command.")
        exit(1)

def need_to_be_created(basic_prompt_file, prompt_data_path):
    path = join(prompt_data_path, basic_prompt_file)
    return not exists(path)

def basic_prompt_file_content_creation(classifier, basic_prompt_file):
    content = ""
    if basic_prompt_file in ("commands.md", "rules.md", "prompt.md"):
        content = get_template_content(classifier, basic_prompt_file)

    if basic_prompt_file == "givens.md":                    
        command = ["ara", "list"]
        output = run(command, capture_output=True, text=True).stdout
        output = output.replace(" - ", " - [ ] ")
        content = output

    return content

def get_template_content(classifier, basic_prompt_file):
    basic_prompt_template_path = f"ara_tools/templates/prompt-creation"
    root, _ = splitext(basic_prompt_file)
    template_name = f"template_{classifier}.md"
    
    root = root.replace("prompt", "prompts")

    template_path = join(basic_prompt_template_path, root, template_name)
    content = ""
    
    if not exists(template_path):
        print(f"WARNING: {template_path} does not exist. Please create a template or {basic_prompt_file} will be empty!")
        return f"# {basic_prompt_file} \n\nNo template found, fill manually or create a template ({template_path})!"

    with open(template_path, 'r') as file:
        return file.read()
    

def create_prompt(classifier, prompt_data_path):
    prompt_file_path = join(prompt_data_path, f"{classifier}.prompt")
    combined_content = ""
    
    md_files = listdir(prompt_data_path)
    md_files = set(filter(lambda file: is_prompt_file(file, prompt_data_path), md_files))
    md_files.remove('givens.md')

    for file_name in md_files:
        md_prompt_file_path = join(prompt_data_path, file_name)
        combined_content += get_file_content(md_prompt_file_path) + "\n\n"

    given_content = "# givens \n\n"
    md_prompt_file_path = join(prompt_data_path, "givens.md")
    for item in extract_checked_items(md_prompt_file_path):
        given_item_path = join("ara", item)
        given_content += get_file_content(given_item_path) + "\n\n"

    combined_content += given_content
    with open(prompt_file_path, 'w') as file:
        file.write(combined_content)


def is_prompt_file(file, prompt_data_path):
    path = join(prompt_data_path, file)
    if exists(path) and file.endswith(".md"):
        return True
    return False


def get_file_content(path):
    with open(path, 'r') as file:
        return file.read()


def get_checked_lines(line):
    return line.startswith("  - [x] ")


def get_path_only(line):
    return line.replace("  - [x] ./", "").strip()


def extract_checked_items(file_path):
    with open(file_path, 'r') as file:

        lines = filter(get_checked_lines, file)
        lines = map(get_path_only, lines)
        lines = set(lines)

    print(lines)
    return lines