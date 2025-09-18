# Detecting Backdoors in Collaboration Graphs of Software Repositories

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd anomaly-detection
```

### 2. Install Python Dependencies
```bash
# For macOS users, install graphviz first:
brew install graphviz
export CFLAGS="-I$(brew --prefix graphviz)/include"
export LDFLAGS="-L$(brew --prefix graphviz)/lib"

# Install Python packages
pip install -r requirements.txt

# Download NLTK data (if needed)
python -c "import nltk; nltk.download('punkt')"
```

### 3. Create Required Directories
```bash
mkdir -p tmp
mkdir -p data/repodata
mkdir -p data/paper/repodata_undirected
mkdir -p data/paper/repodata_undirected_anom
mkdir -p data/paper/repodata_labeled_undirected
```

## System Setup

### Neo4j Database Setup

The system requires a Neo4j database to store and query repository data. Here's how to set it up:

#### Option 1: Docker Setup (Recommended)
```bash
# Remove any existing containers
sudo docker rm $(sudo docker ps -a -q)

# Remove existing Neo4j data
sudo rm -rf $HOME/neo4j/data
sudo rm -rf $HOME/neo4j/plugins

# Start Neo4j container
sudo docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/plugins:/plugins \
  -e NEO4JLABS_PLUGINS='["apoc"]' \
  -e NEO4J_AUTH=neo4j/neo4jj \
  neo4j:3.5.11
```

### Configuration

Update the configuration file at `examples/configs/current_repo.yml`:
```yaml
neo:
  batch_size: 50
  db_pwd: neo4jj          # Your Neo4j password
  db_url: localhost       # Neo4j host
  db_user: neo4j         # Neo4j username
  port: 7687             # Neo4j bolt port
project:
  end_date: null
  index_code: false
  index_developer_email: true
  project_id: your-project-name
  repo: https://github.com/owner/repo  # Will be updated automatically
  start_date: null
```

## Dataset Generation

### Step 1: Prepare Repository URLs

Create a text file with GitHub repository URLs (one per line):

**Example (`data/urls_lists/my_repos.txt`):**
```
https://github.com/owner1/repo1
https://github.com/owner2/repo2
https://github.com/owner3/repo3
```

**Important Notes:**
- Use repositories with sufficient commit history (>50 commits recommended)
- Avoid very large repositories initially (>10K commits) for testing
- Ensure repositories are publicly accessible
- Clean URLs (remove trailing spaces, invalid characters)

### Step 2: Generate Dataset

Edit `src/run_repo_dataset.py` to configure your dataset generation:

```python
# Update these variables at the top of the file:
urls_file_path = os.path.join(file_dir, "..", "data", "urls_lists", "my_repos.txt")

# Configure generation steps
gen_graph = True        # Extract graphs from repositories
process_graph = True    # Process raw graphs into structured format
inject_anom = True      # Inject synthetic anomalies (for training)
```

Run the dataset generation:
```bash
python3 -m src.run_repo_dataset.py
```

**What this does:**
1. **Graph Extraction**: Uses GraphRepo to clone repositories and extract:
   - Developer collaboration networks
   - Commit-file relationships
   - File modification patterns

2. **Graph Processing**: Converts raw data into PyTorch Geometric format:
   - Node features (developer profiles, commit metadata, file statistics)
   - Edge features (collaboration patterns, temporal relationships)

3. **Anomaly Injection**: Adds synthetic backdoor patterns:
   - Type 1: Cross-repository commit injection
   - Type 2: Unusual developer behavior
   - Type 3: Suspicious file modifications
   - Type 4: Temporal anomalies
   - Type 5: Network structure anomalies

## Model Training

### Step 3: Configure Training Parameters

In `src/run_repo_dataset.py`, set the training configuration:

```python
# Training flags
train = True
optimize = False  # Set to True for hyperparameter optimization
tvt_multiple = False  # Set to True for multiple train/test runs

# Model hyperparameters
hp_GVAE = [1e-3, 128, 2, 2, 1e-2, 0.0]
hp_SAD = [1e-3, 128, 2, 2, 1e-2, 0.0, 50, 0.05, 0.5]

# Training epochs
n_epoch_GVAE = 100  # Graph Variational Autoencoder pre-training
n_epoch_SAD = 100   # Deep SAD anomaly detection training
```

### Step 4: Train the Models

The training process involves two stages:

#### Stage 1: GVAE Pre-training
```bash
python3 -m src.run_repo_dataset.py
```

This trains a Graph Variational Autoencoder to learn normal repository patterns:
- Encodes repository graphs into latent representations
- Learns to reconstruct normal development patterns
- Creates a hypersphere center for anomaly detection

#### Stage 2: Deep SAD Training
The system automatically proceeds to Deep SAD training:
- Uses GVAE representations as input
- Trains to distinguish normal vs. anomalous patterns
- Optimizes hypersphere boundary for anomaly detection

**Training Output:**
- Model checkpoints saved in `tmp/YYYY-MM-DD/`
- Training logs with loss curves and metrics
- Center and standard deviation tensors for anomaly scoring

## Model Evaluation and Testing

### Step 5: Test on Known Malicious Repositories

Update the testing configuration in `src/run_repo_dataset.py`:

```python
# Testing flags
test_malicious = True
test_octopus = False
test_all_malicious = False
```

The system will automatically:
1. Load your trained models
2. Process test repositories from `data/urls_lists/urls_list_malicious.txt`
3. Generate anomaly scores
4. Calculate performance metrics (Precision, Recall, F1-Score, ROC-AUC)

### Step 6: Evaluate New Repositories

To test on your own repositories:

1. **Create a test URL list:**
```bash
echo "https://github.com/suspicious/repo" > data/urls_lists/test_repos.txt
```

2. **Update the test configuration:**
```python
# In run_repo_dataset.py, modify the test section:
urls_file_path = os.path.join(file_dir, "..", "data", "urls_lists", "test_repos.txt")
```

3. **Run evaluation:**
```bash
python3 -m src.run_repo_dataset.py
```

### Understanding Results

The system outputs several metrics:
- **Anomaly Score**: Higher values indicate higher likelihood of backdoors
- **ROC-AUC**: Area under ROC curve (higher is better)
- **Precision/Recall**: Standard classification metrics
- **F1-Score**: Harmonic mean of precision and recall

**Interpretation:**
- Scores > 0.7: High likelihood of anomalous patterns
- Scores 0.3-0.7: Moderate suspicion, requires manual review
- Scores < 0.3: Likely benign repository

## Contributors of the paper

- Martin Härterich
- Tom Ganz

## Cite

```
@inproceedings{10.1145/3577923.3583657,
author = {Ganz, Tom and Ashraf, Inaam and H\"{a}rterich, Martin and Rieck, Konrad},
title = {Detecting Backdoors in Collaboration Graphs of Software Repositories},
year = {2023},
isbn = {9798400700675},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3577923.3583657},
doi = {10.1145/3577923.3583657},
abstract = {Software backdoors pose a major threat to the security of computer systems. Minor modifications to a program are often sufficient to undermine security mechanisms and enable unauthorized access to a system. The direct approach of detecting backdoors using static or dynamic program analysis is a daunting task that becomes increasingly futile with the attacker's capabilities. As a remedy, we introduce an orthogonal strategy for the detection of software backdoors. Instead of searching for concealed functionality in program code, we propose to analyze how a software has been developed and locate clues for malicious activities in its version history, such as in a Git repository. To this end, we model the version history as a collaboration graph that reflects how, when and where developers have committed changes to the software. We develop a method for anomaly detection using graph neural networks that builds on this representation and is able to detect spatial and temporal anomalies in the development process. % We evaluate our approach using a collection of real-world backdoors added to Github repositories. Compared to previous work, our method identifies a significantly larger number of backdoors with a low false-positive rate. While our approach cannot rule out the presence of software backdoors, it provides an alternative detection strategy that complements existing work focused only on program analysis.},
booktitle = {Proceedings of the Thirteenth ACM Conference on Data and Application Security and Privacy},
pages = {189–200},
numpages = {12},
keywords = {software repositories, neural networks, anomaly detection},
location = {Charlotte, NC, USA},
series = {CODASPY '23}
}
```
## Contributing
If you wish to contribute code, offer fixes or improvements, please send a pull request. Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

## License
Copyright (c) 2022 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSES/Apache-2.0.txt) file.

