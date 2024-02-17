from os import environ, scandir, makedirs, remove, walk, getenv, rmdir
from os.path import join, exists, isdir, getsize, isfile, getctime
from json import load, dump
from concurrent.futures import ThreadPoolExecutor, wait
from shutil import rmtree
from ara_tools.template_manager import DirectoryNavigator
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document

environ['OPENAI_API_KEY'] = getenv("GPT_KEY")


def add_paths(paths_to_add: list):
    config_file_path="./ara/.vector_db/vector_config.json"
    data = set()

    if exists(config_file_path) and getsize(config_file_path) > 0:
        with open(config_file_path, 'r') as file:
            data = set(load(file))

    for path in paths_to_add:
        add_path_if_exists(data, path)
    
    if data:
        update_db_for_paths(data)
    

def update_db_for_paths(data):
    config_file_path="./ara/.vector_db/vector_config.json"
    with open(config_file_path, 'w') as file:
        dump(list(data), file, indent=4)
    init_DB()


def add_path_if_exists(data, path):
    if not exists(path):
        print(f"{path} does not exist")
        return
    data.add(path)


def embeddings(document):
    parent_directory = "ara"
    hidden_directory = ".vector_db"
    full_path = join(parent_directory, hidden_directory)

    if not exists(full_path):
        makedirs(full_path)

    embeddings = OpenAIEmbeddings()
    chromadb = Chroma.from_documents(document, embeddings, persist_directory=full_path)
    return chromadb



def loadembeddings():
    parent_directory = "ara"
    hidden_directory = ".vector_db"
    full_path = join(parent_directory, hidden_directory)

    embeddings = OpenAIEmbeddings()
    chromadb_2 = Chroma(persist_directory=full_path, embedding_function=embeddings)
    return chromadb_2


def read_json(path):
    with open(path, 'r') as file:
        return load(file)



def process_document(file_path):
    loader = TextLoader(file_path)

    if "./ara/.vector_db/" in file_path:
        return

    documents = loader.load()

    if documents:
        return embeddings(documents)

    return None


def process_entry(entry, current_depth):
    if entry.is_dir(follow_symlinks=False):
        list_files(entry.path, current_depth + 1)
    if entry.is_file():
        process_document(entry.path)
    if not exists(entry.path):
        print(f"{entry.path} does not exist")


def list_files(start_path, current_depth=0):
    if isfile(start_path):
        process_document(start_path)
        return

    with ThreadPoolExecutor() as executor:
        with scandir(start_path) as entries:
            futures = [executor.submit(process_entry, entry, current_depth) for entry in entries]
            wait(futures)


def process_paths(file_paths):
    if not file_paths:
        print("vectorDB successfully initialized.")
        return

    path = file_paths[0]
    if not exists(path):
        print(f"{path} does not exist")
        return
    
    list_files(path)
    process_paths(file_paths[1:])


def create_DB():
    config_file_path = "./ara/.vector_db/vector_config.json"

    if exists(config_file_path):
        init_DB()
        return

    makedirs("./ara/.vector_db")

    with open(config_file_path, "x") as file:
        file.write('[]')
    print("vectorDB config file successfully created.")


def update_DB():
    config_file_path = "./ara/.vector_db/vector_config.json"

    if not exists(config_file_path):
        create_DB()
        return
    
    init_DB()


def init_DB():
    config_file_path = "./ara/.vector_db/vector_config.json"

    with open(config_file_path, 'r') as file:
        file_paths = load(file)
        if file_paths == []:
            print("vector config contains no paths.")
            return
        process_paths(file_paths)


def reset_DB():
    directory = './ara/.vector_db'
    file_to_keep = 'vector_config.json'
    full_path_to_keep = join(directory, file_to_keep)

    if not exists(full_path_to_keep):
        create_DB()

    paths_to_delete = []
    all_paths_in_directory = list(walk(directory, topdown=False))

    for root, dirs, files in all_paths_in_directory:
        paths_to_delete.extend(join(root, f) for f in files if join(root, f) != full_path_to_keep)
        paths_to_delete.extend(join(root, d) for d in dirs)

    file_paths = list(filter(isfile, paths_to_delete))
    dir_paths = list(filter(isdir, paths_to_delete))

    list(map(remove, file_paths))
    list(map(rmtree, dir_paths))

    print("vectorDB successfully reset.")



def reset_config():
    if exists("./ara/.vector_db/vector_config.json"):
        with open("./ara/.vector_db/vector_config.json", 'w') as file:
                file.write('[]')
        print("vectorDB config successfully reset.")
        return


def search_DB(amount, query):
    if not exists("./ara/.vector_db/chroma.sqlite3"):
        init_DB()
        return
    db = loadembeddings()
    docs = db.similarity_search(query, amount)
    metadata_content = ""
    metadata_content += f'Query: "{query}"\n\n'
    count = 0

    metadata_content += "\n".join(
        f'{i + 1}. "{result.metadata.get("source", "No source available")}"'
        for i, result in enumerate(docs)
    )

    with open("./ara/.vector_db/recommendations-vector.md", 'w') as file:
        file.write(metadata_content)