
'''
	python3 status.proc.py "status_3.py"
'''

import law_dictionary

def check_1 ():
	dictionary = {
		"directory_1": "/some/path"
	}

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

	assert (dictionary ["directory_1"] == "/some/path")
	assert (dictionary ["directory_2"] == "/drives")


checks = {
	"Doesn't run the contingency if not required and provided": check_1
}