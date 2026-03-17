# Notes Claude / Development Process

development process writes tests!?

## tests
tests gaps: 
parameters with multiple types: add multiple tests (at least one per type). e.g. list_documents with parameter modified_after 
nonsense values: list_documents with checksum="hello world" => delivered a full return list, because api parameter was wrong (and then ignored)



looks like: upload_document has no custom fields, upload document has no owner field?!



todo: test the https:// connection to my live instance.

## documentation
refer in parameters "matching_algorithm" to the class MatchingAlgorithm: e.g. storage_paths.create(), tags.create()
date filter in documents.list(): say something about the iso format!?
documents.list(): custom_field_query - format? examples?

documents.upload(): poll_interval, poll_timeout in seconds?

documents.bulk_edit(): add remark again "better use high-level methods", add full list of implemented methods. say explicitly that not all methods were implemented.


## general features

client.documents.list(): archive_serial_number => null => filter for archive_serial_number__isnull=TRUE

documents.bulk_modify_tags(): test edge case of mixed int/str param "add_tags". 

tags.create() - can't find param "parent" in the api. later version of paperless-ngx?

logging needs to be added.

custom_fields.update(): param "extra_data" needs attention: -> typing.Any, vague documentation of the format.


after issue 0019 was implemented: I'm not sure if UNSET is necessary for the documents.upload method.


# History of notes

### None Topic
update document: owner = None should be forwarded to the api as owner = null => deleting owner!
solve with pydantic
=> see issue 0019

### parameter completeness:
correspondents: 
    missing fields in update(): "owner", "set_permissions"
custom_fields: 
    missing fields in list(): "name_contains", "name_exact"
    missing in update(): "data_type
document_types:
    missing fields in update(): "owner", "set_permissions"
documents
    missing fields in list(): "document_type_name_exact", "document_type_name_contains"
    missing fields in update(): "remove_inbox_tags"
    upload(): "custom_fields"
storage_paths
    missing fields in list(): "path_exact", "path_contains"
    missing fields in update(): "owner", "set_permissions" (available in the user interface - not shown in my api documentation)
tags
    missing fields in update(): "owner", "set_permissions"
=> see issue 0020

### document related tasks
check: archive_serial_number sometimes abbreviated as asn? here: documents.update(), documents.upload()

in documents.update() parameter is called date. should be called "created" 

search_mode should not be "title_or_text" but "title_or_content" - stick to the name of field "content"!

documents.upload(): created should accept either date or str. currently only string.

=> see issue 0021

###
in correspondents.create(), document_types.create() and storage_paths.create() and tags.create() -> parameter "is_insensitive" is None by default. this means the parameter is omitted. the api default is "true" afik. i think it is better to set the default to "true" instead of None. so that the user is aware of the actual behaviour. doesn't apply to the update() methods because there "None" means - don't change it. Thats ok.


## 16.03.


add issue: fix defaults
enable configuration: what are the defaults? - perhaps a mcp server topic!?

add issue: return value should contain top level info. 



## general: 
keep the None / Unset usage. 
create a public alias for _Unset and use it in the signatures to make the pdoc documentation more readable. (i want to see: "owner: int | None | Unset = UNSET")

`` python
# in easypaperless/__init__.py or a public types module
from easypaperless._internal.sentinel import _Unset

Unset = _Unset  # public alias
``


## functions:

### correspondents: 
list(): 
use "ids: List[int] | None = None " instead of the code with Optional[]

get(): ok

create(): 
match: can't be None - remove the code that handels None. (None currently means use the default)
matching_algorithm: can't be None - remove the code that handels None. (None currently means use the default)
set_permissions: can't be None, default unset?

update():
name: cant be none
match: can't be None
matching_algorithm: can't be None
is_insensitive: can't be None
set_permissions: can't be None, default unset?

delete() ok
bulk_delete: ok

bulk_set_permissions(): 
set_permissions: can't be None, default unset?
owner: can be None, default must be Unset


### custom_fields:
list(): ok
get(): ok
create(): 
set_permissions: can't be None, default unset?

update(): 
name can't be None
data_type cant be None

missing parameters owner and set_permissions!

delete: ok


### document_types

list(): 
use "ids: List[int] | None = None " instead of the code with Optional[]

get(): ok
create():
	match: can't be None - remove the code that handels None. (None currently means use the default)
	matching_algorithm: can't be None - remove the code that handels None. (None currently means use the default)
	set_permissions: can't be None, default unset?

update():
	name: cant be none
	match: can't be None
	matching_algorithm: can't be None
	is_insensitive: can't be None
	set_permissions: can't be None, default unset?

delete() ok
bulk_delete ok

bulk_set_permissions(): 
	set_permissions: can't be None, default unset?
	owner: can be None, default must be Unset


### documents

get() ok
get_metadata() ok
list(): 
	remove all usage of Optional[] replace by type | None 
update():
	title cant be None
	content cant be none
	tags = None should be translated to empty list?
	set_permissions: can't be None, default unset?

delete() ok
download() ok
upload()
	title: can't be None, default unset?
	tags: don't use Optional[] replace by type | None 
	custom_fields: don't use Optional[] replace by type | None 

 bulk_add_tag: ok
 bulk_add_tag: ok
 bulk_modify_tags: remove Optional[] replace by type | None 

 bulk_delete: ok
 bulk_set_correspondent: ok
 bulk_set_document_type : ok
 bulk_set_storage_path: ok
 bulk_modify_custom_fields: remove Optional[] replace by type | None 

 bulk_set_permissions
	set_permissions: can't be None, default unset?
	owner: can be None, default must be Unset , None to clear

### documents.notes

list(): ok
create(): ok 
delete(): ok

### StoragePaths:
list(): remove Optional[] replace by type | None 
get(): ok
create(): 
	path can't be None
	match: can't be None - remove the code that handels None. (None currently means use the default)
	matching_algorithm: can't be None - remove the code that handels None. (None currently means use the default)
	set_permissions: can't be None, default unset?
update():
	name: can't be None
	path: can't be None
	match: can't be None
	matching_algorithm: can't be None
	is_insensitive: can't be None
	set_permissions: can't be None, 

	
	
delete(): Ok
bulk_delete(): ok
bulk_set_permissions():
	set_permissions: can't be None, default unset?
	owner: can be None, default must be Unset
	
### Tags:

list(): remove Optional[] replace by type | None 
get(): ok
create(): 
	color: can't be none, default Unset
	is_inbox_tag: can't be none, default Unset
	match: can't be None - remove the code that handels None. (None currently means use the default)
	matching_algorithm: can't be None - remove the code that handels None. (None currently means use the default)
	set_permissions: can't be None, default unset?
update():
	name: can't be none
	color: cant' be none
	is_inbox_tag: can't be none
	match: can't be none
	matching_algorithm: can't be none
	is_insensitive: can't be none
	set_permissions: can't be none
	
	
delete(): Ok
bulk_delete(): ok
bulk_set_permissions():
	set_permissions: can't be None, default unset?
	owner: can be None, default must be Unset

## offtopic
remarks: mcp: ordering param: add possible fields to the description.
bulk_set_permissions() merge param desc!?
custom_fields.create(): extra_data desc?!
storage_paths.create(): path desc?!


check again: documents.get_metadata() - working?


not sure about set permissions

paperless-ngx fehler? created sollte nullable sein!?

client poll_intervall and poll_timeout : docstring has hint "in seconds"?


bulk_set_permissions in documents lead to an error 500 (when tested via the mcp server).








## 17.03.2026

oh wow: set permissions in client.py -> create resource and update resource - check implementation!?