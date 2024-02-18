
'''
	python3 status.proc.py "status_broken_1.py"
'''

import law_dictionary

def broken_1 ():
	def obstacle (prob):
		return prob


	dictionary = {}
	the_obstacle = law_dictionary.check (	
		laws = {
			"directory": {
				"required": True,
				"contingency": "/",
				"allow": [ "/" ]
			}
		},
		dictionary = dictionary,
		obstacle = obstacle		
	)
	
	print ("the obstacle:", the_obstacle)
	
	assert (
		the_obstacle == 
		'The label "directory" was not found in the laws.'
	)
	

def broken_2 ():
	def obstacle (prob):
		return prob

	dictionary = {
		"directory": "/",
		"directory 2": "/"
	}
	
	the_obstacle = law_dictionary.check (	
		laws = {
			"directory": {
				"required": True,				
				"allow": [ "" ]
			},
			"directory 2": {
				"required": True,
				"allow": [ "/" ]
			}
		},
		dictionary = dictionary,
		
		obstacle = obstacle
	)
	
	print ("the obstacle:", the_obstacle)
	
	assert (
		the_obstacle == 
		'Defintion "/" is not allowed.'
	)
	

checks = {
	'broken 1': broken_1,
	'broken 2': broken_2
}

