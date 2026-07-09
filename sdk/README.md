# bioapi-sdk

Python SDK client for the BioAPI genomics REST service.

The distribution package is named `bioapi-sdk` and the import package is `bioapi_sdk`.

## Installation

```bash
pip install bioapi-sdk
```

## Usage

```python
from bioapi_sdk import gene_symbols, information_of_genes

symbols = gene_symbols(["ENSG00000141510", "7157"])
genes = information_of_genes(["TP53"])
```

By default, requests are sent to `https://bioapi.multiomix.org`. You can change
the server per call with `base_url=` or globally with the `BIOAPI_BASE_URL`
environment variable.

```python
from bioapi_sdk import gene_symbols

symbols = gene_symbols(["TP53"], base_url="http://localhost:5000")
```

## Error handling

The SDK raises `BioAPIRequestError` when an API request cannot be completed.
This includes temporary service or gateway failures: if BioAPI returns a non-JSON error response, such as an HTTP 502, the error states that BioAPI is currently unavailable and includes the HTTP status code instead of reporting a JSON parsing error.

```python
from bioapi_sdk import BioAPIRequestError, gene_symbols

try:
    symbols = gene_symbols(["TP53"])
except BioAPIRequestError as exc:
    print(exc)  # BioAPI is currently unavailable (HTTP 502 Bad Gateway).
```

## MCP server

The SDK package also includes a BioAPI MCP server for LLM clients. Install the MCP extra to include the MCP runtime dependency:

```bash
pip install "bioapi-sdk[mcp]"
```

After installation, run the server over stdio with:

```bash
bioapi-mcp
```

## Development

Build the package from this directory:

```bash
python -m build
```

The core SDK intentionally depends only on `requests` at runtime. The MCP server dependencies are installed only with the `mcp` extra.
