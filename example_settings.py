BIND: '0.0.0.0'
PORT: 1965
AUTO_INDEX: true
DOCUMENT_ROOT: /path/to/gemini_docs
INDEX_FILE: index.gmi
MIME_TYPES:
  'text/gemini':
    - .gmi
    - .gemini
SSL:
  CA: /path/to/fullchain.pem
  CERT: /path/to/cert.pem
  PRIVATE_KEY: /path/town/privkey.pem