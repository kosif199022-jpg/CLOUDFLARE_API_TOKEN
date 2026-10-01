# Artifact QA v4

Transport/generation success is not completion. Final deliverables need type-specific checks when available:
- JSON: parse successfully.
- DOCX: valid OPC ZIP containing `[Content_Types].xml` and `word/document.xml`; visual/semantic review remains separate.
- XLSX: valid OPC ZIP with workbook structure; formulas/charts/pivots need deeper spreadsheet-specific verification when used.
- PPTX: valid OPC ZIP with presentation structure; render/placeholder/layout review is still required when visual quality matters.
- PDF: structural/header validation plus render/readability inspection when possible.
- Code/text: secret scan + language/build/tests/security checks via Code Master/Delivery Gate.

`artifact_qa.py` is a deterministic first gate, not a substitute for visual review or business correctness.
