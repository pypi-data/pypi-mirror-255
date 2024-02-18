from localstack.utils.numbers import is_number,to_number
from pyparsing import Group,OneOrMore,Word,alphanums,alphas,delimitedList,nestedExpr,originalTextFor,printables,quotedString
def parse_comma_separated_variable_assignments(expr):
	A=quotedString|originalTextFor(OneOrMore(Word(printables,excludeChars='(),')|nestedExpr()));D=Word(alphas+'_',alphanums+'_');E=Group(D+Word('=')+A);F=delimitedList(E);G=F.parseString(expr).asList();C={}
	for H in G:
		B,I,A=H;B=B.strip();A=A.strip()
		if len(A)>=2 and A[0]==A[-1]=="'":A=A.strip("'")
		elif len(A)>=2 and A[0]==A[-1]=='"':A=A.strip('"')
		elif is_number(A):A=to_number(A)
		C[B]=A
	return C