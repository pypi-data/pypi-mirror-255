Mutalyzer3 API.

# Installation

    pip install mutalyzer-api

# Enable the cache

Create a cache folder and a configuration file.

    mkdir cache
    echo MUTALYZER_CACHE_DIR = \'$(pwd)/cache\' > config.txt

Populate the cache.

    mutalyzer_retriever --id NC_000022.11 --parse > cache/NC_000022.11

# Running

Start the backend.

    MUTALYZER_SETTINGS="$(pwd)/config.txt" mutalyzer_api

Navigate to `http://localhost:5000/api` to interact with the API.
