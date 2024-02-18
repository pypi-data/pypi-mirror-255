
'''
	python3 status.proc.py "status_2.py"
'''

import law_dictionary

def check_1 ():
	dictionary = {}

	def retrieve_directory ():
		return "/"

	report = law_dictionary.check (	
		return_obstacle_if_not_legit = True,
		laws = {
			"directory_1": {
				"required": False,
				"contingency": retrieve_directory,
				"type": str
			},
			"directory_2": {
				"required": False,
				"contingency": "/drives",
				"type": str
			}
		},
		dictionary = dictionary
	)
	if (report ["advance"] != True):
		raise Exception (report ["obstacle"])	

	assert (dictionary ["directory_1"] == "/")
	assert (dictionary ["directory_2"] == "/drives")

def check_2 ():
	dictionaries = [{ "directory_1": "/" }, { "directory_1": "/drives"  }]

	for dictionary in dictionaries:
		law_dictionary.check (	
			laws = {
				"directory_1": {
					"required": True,
					"allow": [ "/", "/drives" ]
				}
			},
			dictionary = dictionary
		)

def check_3 ():
	dictionary = { 
		"paths": {
			"directory_1": "/" 
		}
	}	
		
	law_dictionary.check (	
		laws = {
			"paths": {
				"required": True,
				"type": dict
			}
		},
		dictionary = dictionary
	)

	law_dictionary.check (	
		laws = {
			"directory_1": {
				"required": True,
				"type": str
			}
		},
		dictionary = dictionary ["paths"]
	)

checks = {
	'check 1': check_1,
	'check 2': check_2,
	'check 3: multiple levels': check_3
}