# Documents Folder

This folder contains the documents that will be processed by the RAG system.

## Supported File Types:
- **PDF files** (.pdf) - Program documentation, manuals
- **Text files** (.txt) - Plain text documents
- **Markdown files** (.md) - Formatted documentation
- **CSV files** (.csv) - Structured data that will be converted to searchable text

## Usage:
1. Place your documents in this folder
2. Use the Slack bot admin commands to process them
3. Documents will be automatically chunked and indexed in ChromaDB

## File Size Limit:
- Maximum file size: 50MB per file
- For larger files, consider splitting them into smaller parts

## Examples:
```
documents/
├── program_guide.pdf
├── faq.md
├── user_manual.txt
└── data_specifications.csv
```

## Processing:
Documents placed here can be processed using:
- Slack command: `/upload-doc filename.pdf`
- Admin interface in the bot
- Automatic processing when files are detected