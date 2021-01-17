HOST: '0.0.0.0'
ALIASES:
  - banjo.town
  - magicians.band
PORT: 1965
AUTO_INDEX: true
DOCUMENT_ROOT: /home/skyron/skyron-dev/gemini_docs
INDEX_FILE: index.gmi
MIME_TYPES:
  'text/gemini':
    - .gmi
    - .gemini
SSL:
  CA: /etc/letsencrypt/live/banjo.town/fullchain.pem
  CERT: /etc/letsencrypt/live/banjo.town/cert.pem
  PRIVATE_KEY: /etc/letsencrypt/live/banjo.town/privkey.pem
# TODO: support for virtual hosts 