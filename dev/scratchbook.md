# Notes Claude / Development Process

development process writes tests!?
tests gaps: 
parameters with multiple types: add multiple tests (at least one per type). e.g. list_documents with parameter modified_after 
nonsense values: list_documents with checksum="hello world" => delivered a full return list, because api parameter was wrong (and then ignored)

logging needs to be added.

looks like: upload_document has no custom fields, upload document has no owner field?!

update document: owner = None should be forwarded to the api as owner = null => deleting owner!
solve with pydantic

list_documents parameter "custom_field_query" needs better documentation.
in general: pdoc documentation in not well formated.

