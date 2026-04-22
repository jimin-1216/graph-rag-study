// Neo4j seed loader for law-open-data normalized outputs.
// Assumption:
// - legal_documents.csv
// - legal_units.csv
// - legal_relations.csv
// are copied into Neo4j's import directory.

CREATE CONSTRAINT legal_document_id IF NOT EXISTS
FOR (d:LegalDocument)
REQUIRE d.document_id IS UNIQUE;

CREATE CONSTRAINT legal_unit_id IF NOT EXISTS
FOR (u:LegalUnit)
REQUIRE u.unit_id IS UNIQUE;

CREATE CONSTRAINT legal_reference_key IF NOT EXISTS
FOR (r:LegalReference)
REQUIRE r.reference_key IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///legal_documents.csv' AS row
MERGE (d:LegalDocument {document_id: row.`document_id:ID(LegalDocument)`})
SET d.slug = row.slug,
    d.title = row.title,
    d.document_type = row.document_type,
    d.department = row.department,
    d.promulgation_date = row.promulgation_date,
    d.effective_date = row.effective_date,
    d.law_id = row.law_id,
    d.mst = row.mst,
    d.rule_id = row.rule_id,
    d.kind = row.kind;

LOAD CSV WITH HEADERS FROM 'file:///legal_units.csv' AS row
MERGE (u:LegalUnit {unit_id: row.`unit_id:ID(LegalUnit)`})
SET u.document_id = row.document_id,
    u.parent_unit_id = row.parent_unit_id,
    u.unit_type = row.unit_type,
    u.unit_no = row.unit_no,
    u.title = row.title,
    u.text = row.text,
    u.effective_date = row.effective_date,
    u.raw_key = row.raw_key;

LOAD CSV WITH HEADERS FROM 'file:///legal_relations.csv' AS row
WITH row
WHERE row.`:TYPE` = 'HAS_UNIT'
MATCH (d:LegalDocument {document_id: row.`:START_ID`})
MATCH (u:LegalUnit {unit_id: row.`:END_ID`})
MERGE (d)-[:HAS_UNIT]->(u);

LOAD CSV WITH HEADERS FROM 'file:///legal_relations.csv' AS row
WITH row
WHERE row.`:TYPE` = 'HAS_CHILD'
MATCH (source:LegalUnit {unit_id: row.`:START_ID`})
MATCH (target:LegalUnit {unit_id: row.`:END_ID`})
MERGE (source)-[:HAS_CHILD]->(target);

LOAD CSV WITH HEADERS FROM 'file:///legal_relations.csv' AS row
WITH row
WHERE row.`:TYPE` = 'CITES_ARTICLE_TEXT'
OPTIONAL MATCH (sourceDoc:LegalDocument {document_id: row.`:START_ID`})
OPTIONAL MATCH (sourceUnit:LegalUnit {unit_id: row.`:START_ID`})
WITH row, coalesce(sourceDoc, sourceUnit) AS source
WHERE source IS NOT NULL
MERGE (ref:LegalReference {
  reference_key: row.`:END_ID`,
  reference_type: 'ARTICLE_TEXT'
})
MERGE (source)-[r:CITES_ARTICLE_TEXT]->(ref)
SET r.source_text = row.source_text;

LOAD CSV WITH HEADERS FROM 'file:///legal_relations.csv' AS row
WITH row
WHERE row.`:TYPE` = 'REFERS_TO_LAW_NAME'
OPTIONAL MATCH (sourceDoc:LegalDocument {document_id: row.`:START_ID`})
OPTIONAL MATCH (sourceUnit:LegalUnit {unit_id: row.`:START_ID`})
WITH row, coalesce(sourceDoc, sourceUnit) AS source
WHERE source IS NOT NULL
MERGE (ref:LegalReference {
  reference_key: row.`:END_ID`,
  reference_type: 'LAW_NAME'
})
MERGE (source)-[r:REFERS_TO_LAW_NAME]->(ref)
SET r.source_text = row.source_text;

LOAD CSV WITH HEADERS FROM 'file:///legal_relations.csv' AS row
WITH row
WHERE row.`:TYPE` = 'IMPLEMENTS_CANDIDATE'
MATCH (source:LegalDocument {document_id: row.`:START_ID`})
MERGE (ref:LegalReference {
  reference_key: row.`:END_ID`,
  reference_type: 'DOCUMENT_TITLE'
})
MERGE (source)-[r:IMPLEMENTS_CANDIDATE]->(ref)
SET r.source_text = row.source_text;

// Convenience links from each unit to its owning document.
MATCH (u:LegalUnit)
MATCH (d:LegalDocument {document_id: u.document_id})
MERGE (u)-[:BELONGS_TO]->(d);
