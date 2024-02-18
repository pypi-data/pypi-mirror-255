import os
import sys
import shutil
import urllib
import zipfile
import subprocess
from pathlib import Path
from dataclasses import dataclass


# Supported Environments
KAGGLE = "Kaggle" 
GOOGLE_COLAB = "Google-Colab"

# Default variables (feel free to change them from the notebook if you need it)
gdrive_keys_path = "/content/drive/MyDrive/.keys/"
gdrive_kaggle_key_fname = "kaggle.json"
gdrive_github_key_fname = "github-token.txt"
kaggle_github_token_secret = 'github-token'

# Dataclasses
@dataclass
class GitHubRepo:
    name: str
    owner: str
    install_requirements: bool = True

    
class ZippedDataset:
    
    def __init__(self, url:str, name:str, dest:str, unzip:bool=True, remove_zip:bool=True) -> None:
        self.url = url
        self.name = name
        self.dest = dest
        self.unzip = unzip
        self.remove_zip = remove_zip
    
    @property
    def dest_path(self):
        return str(Path(self.dest) / self.name)
    

class KaggleDataset(ZippedDataset):
    
    def __init__(self, name:str, owner:str, dest:str, unzip:bool=True, remove_zip:bool=True) -> None:
        self.name = name
        self.owner = owner
        self.dest = dest
        self.unzip = unzip
        self.remove_zip = remove_zip
        super().__init__(\
            f"{self.owner}/{self.name}", self.name, self.dest, self.unzip, self.remove_zip)

# ===================== Utility Functions =====================
# =============================================================
def in_kaggle():
    return 'KAGGLE_KERNEL_RUN_TYPE' in os.environ


def in_google_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False

      
def get_environment():
    if in_kaggle(): return KAGGLE
    elif in_google_colab(): return GOOGLE_COLAB
    return None


def execute_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return stdout.decode()
        else:
            return stderr.decode()
    except Exception as e:
        return f"Error: {e}"
    
# =============================================================
    
# ======================= Main Functions ======================
# =============================================================
def setup_environment(github_repo:GitHubRepo=None, dataset:ZippedDataset=None) -> str:
    environment = get_environment()
    print("[%] Detected Environment:", environment)
    if (environment == GOOGLE_COLAB or environment == KAGGLE) and github_repo is not None:
        GITHUB_TOKEN = None
        # Load GitHub token
        if environment == KAGGLE:
            from kaggle_secrets import UserSecretsClient
            user_secrets = UserSecretsClient()
            try:
                GITHUB_TOKEN = user_secrets.get_secret(kaggle_github_token_secret)
            except:
                print(f"[!] Github token secret '{kaggle_github_token_secret}' was not found, " + 
                     "make sure that the secret variable is attached to the notebook")
        elif environment == GOOGLE_COLAB:
            # Retrieve GitHub token
            github_token_path = gdrive_keys_path+gdrive_github_key_fname
            if os.path.exists(github_token_path):
                with open(github_token_path, 'r') as file:
                    GITHUB_TOKEN = file.read().strip().removesuffix("\n")
            else:
                print(f"GitHub token was not found in '{github_token_path}'")
            # Move kaggle.json to ~/.kaggle 
            kaggle_token_path = gdrive_keys_path+gdrive_kaggle_key_fname
            gc_dir = Path.home()/".kaggle/"
            os.makedirs(gc_dir, exist_ok=True)
            final_path = gc_dir/gdrive_kaggle_key_fname
            if not os.path.exists(final_path):
                shutil.copy(kaggle_token_path, str(final_path))
            else:
                print(f"[!] '{gdrive_kaggle_key_fname}' already exists at {gc_dir}")
        clone_github_repo(github_repo, token=GITHUB_TOKEN)
    
    dataset_path = None
    if dataset is not None:
        dataset_path = download_dataset(dataset, environment=environment)
        
    return dataset_path


def download_dataset(dataset:ZippedDataset, environment):
    if environment == KAGGLE:
        dataset.dest = '/kaggle/input/'
        if not os.path.exists(dataset.dest_path):
            print(f"[!] '{dataset.dest_path}' was not found, remember to manually upload the dataset")
    elif not os.path.exists(dataset.dest_path):
        print(f"[%] Downloading '{dataset.name}' dataset from '{dataset.url}'...")
        zip_file = f'{dataset.name}.zip'
        
        if isinstance(dataset, KaggleDataset):
            execute_command(f'kaggle datasets download -d {dataset.url}')
        elif isinstance(dataset, ZippedDataset):
            urllib.request.urlretrieve(dataset.url, zip_file)
        else:
            raise TypeError("dataset must be of type ZippedDataset")
            
        if dataset.unzip:
            print(f"[%] Unzipping data to {dataset.dest_path}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(dataset.dest_path)
            
        if dataset.remove_zip:
            print("[%] Removing zip file")
            os.remove(zip_file)
    else:
        print(f"[%] Dataset already downloaded at '{dataset.dest_path}'")
    
    return dataset.dest_path
    
    
def clone_github_repo(repo:GitHubRepo, token:str=None):
    token_part = ""
    if token:
        token_part = f"{repo.owner}:{token}@"
    clone_url = f"https://{token_part}github.com/{repo.owner}/{repo.name}.git"
    if os.path.exists(repo.name):
        print(f"[%] Deleting exisiting repo '{repo.name}'")
        shutil.rmtree(repo.name)
    print(f"[%] Cloning '{repo.name}', token={token is not None}")
    output = execute_command(f"git clone {clone_url}")
    if output.strip().removesuffix("\n") != "":
        print(output)
    # Append path of cloned project so that imports can be used normally
    print(f"[%] Adding '{repo.name}' repo to Python Path")
    sys.path.append(f"{repo.name}")
    # Install project requirements if present
    if repo.install_requirements:
        req_path = Path(repo.name)/"requirements.txt"
        if req_path.exists():
            print("[%] Installing requirements.txt...")
            output = execute_command(f"pip3 install -r {req_path} --quiet")
            if output.strip().removesuffix("\n") != "":
                print(output)
            print("[%] Requirements installed")
        else:
            print(f"[!] Aborting requirements installation, '{req_path}' was not found")

# =============================================================