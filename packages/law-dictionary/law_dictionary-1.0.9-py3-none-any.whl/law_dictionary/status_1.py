
'''
	python3 status.proc.py "modules/law_dictionary/status_1.py"
'''

import law_dictionary

def check_1 ():
	def retrieve_directory ():
		return "/"

	dictionary = {}
	law_dictionary.check (	
		laws = {
			"directory": {
				"required": False,
				"type": str,
				"contingency": retrieve_directory
			}
		},
		dictionary = dictionary
	)
	
	assert (len (dictionary) == 1)
	assert (dictionary ["directory"] == "/")

def check_2 ():
	dictionary = {}
	law_dictionary.check (	
		laws = {
			"directory": {
				"required": False,
				"contingency": "/",
				"type": str
			}
		},
		dictionary = dictionary
	)
	
	assert (len (dictionary) == 1)
	assert (dictionary ["directory"] == "/")

def check_3 ():
	dictionary = {}
	law_dictionary.check (	
		laws = {
			"directory": {
				"required": False,
				"contingency": "/",
				"allow": [ "/" ]
			}
		},
		dictionary = dictionary
	)
	
	assert (len (dictionary) == 1)
	assert (dictionary ["directory"] == "/")

def check_4 ():
	dictionary = {
		"a field": "this is anoter field"
	}
	law_dictionary.check (	
		allow_extra_fields = True,
		laws = {},
		dictionary = dictionary
	)
	
	assert (len (dictionary) == 1)
	assert (dictionary ["a field"] == "this is anoter field")

def check_5 ():
	dictionary = {}
	law_dictionary.check (	
		allow_extra_fields = True,
		laws = {
			"extension": {
				"required": False,
				"contingency": ".s.HTML",
				"type": str
			}
		},
		dictionary = dictionary
	)
	
	assert (len (dictionary) == 1)
	assert (dictionary ["extension"] == ".s.HTML")

checks = {
	'check 1, non-required with contingency': check_1,
	'check 2, non-required with contingency and type': check_2,
	'check 3, non-required with contingency and allow': check_3,
	'check 4': check_4,
	'check 5': check_5
}