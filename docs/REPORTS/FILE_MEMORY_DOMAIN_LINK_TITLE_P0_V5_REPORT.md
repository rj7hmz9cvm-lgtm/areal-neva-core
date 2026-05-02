# FILE_MEMORY_DOMAIN_LINK_TITLE_P0_V5_REPORT

generated_at: 2026-05-02T13:28:20+03:00

status: OK

fixed:
- _fm_item_domain: file_name has priority before mixed hay/value search
- _fm_public_links: public links are taken only from item["links"], not from value/summary/result/raw_input blobs
- _fm_public_title: leading numeric prefix removed from file_name

verified:
- КЖ/КД/КМ/КМД/АР/project file names classify as project
- smeta/VOR file names classify as estimate
- links from unrelated blob text are not shown
- leading "4. " removed from title
- telegram_daemon.py not modified
- no live Telegram run
- worker active without fatal tracebacks
