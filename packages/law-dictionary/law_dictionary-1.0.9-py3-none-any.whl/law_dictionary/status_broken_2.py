
'''
	python3 status.proc.py "status_broken_2.py"
'''

import law_dictionary

def broken_1 ():
	dictionary = {
		"directory_1": "/",
		"directory_2": "/drives"
	}
	report = law_dictionary.check (
		return_obstacle_if_not_legit = True,
		allow_extra_fields = False,
		laws = {
			"directory_1": {
				"required": True
			}
		},
		dictionary = dictionary
	)
	if (report ["advance"] != True):
		pass;
	
	assert (report ["advance"] == False), report
	assert (report ["obstacle"] == 'The label "directory_2" was found in the dictionary but not in the laws.'), report


checks = {
	'broken 1': broken_1
}

