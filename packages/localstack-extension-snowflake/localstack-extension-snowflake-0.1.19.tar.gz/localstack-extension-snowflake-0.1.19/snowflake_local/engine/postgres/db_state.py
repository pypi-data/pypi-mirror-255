import dataclasses
@dataclasses.dataclass
class IdentifierOverrides:
	entries:list[tuple[str,str,str]]=dataclasses.field(default_factory=list)
	def find_match(E,database,schema,obj_name):
		D=obj_name;C=schema;B=database
		for A in E.entries:
			if B and A[0]and B.lower()!=A[0].lower():continue
			if C and A[1]and C.lower()!=A[1].lower():continue
			if D and A[2]and D.lower()!=A[2].lower():continue
			return A
class State:server=None;initialized_dbs=[];identifier_overrides=IdentifierOverrides()