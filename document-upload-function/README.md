```sql
CREATE TABLE file_translation_logs (
    file_name TEXT PRIMARY KEY,
    landing_zone_path TEXT,
    file_type TEXT CHECK (file_type IN ('pdf', 'docx')),
    upload_date DATE,
    upload_datetime TIMESTAMP,
    upload_status TEXT CHECK (upload_status IN ('failed', 'in progress', 'done')),
    translation_date DATE,
    translation_datetime TIMESTAMP,
    translation_status TEXT CHECK (translation_status IN ('failed', 'in progress', 'done')),
    translated_zone_path TEXT,
    fromLanguage TEXT,
    toLanguage TEXT,
    watermark_date DATE,
    watermark_datetime TIMESTAMP,
    watermark_status TEXT CHECK (watermark_status IN ('failed', 'in progress', 'done')),
    watermark_zone_path TEXT,
    glossary_content JSON,
    glossary_processing_status TEXT CHECK (glossary_processing_status IN ('failed', 'in progress', 'done')),
    glossary_zone_path TEXT,
    uploaded_by TEXT,
    statue INTEGER
);

CREATE INDEX idx_file_name ON file_translation_logs (file_name);
```