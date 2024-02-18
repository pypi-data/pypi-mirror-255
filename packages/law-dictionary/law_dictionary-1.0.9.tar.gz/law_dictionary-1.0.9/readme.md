




******

Bravo!  You have received a Mercantilism Diploma in "law_dictionary" from   
the Orbital Convergence University International Air and Water 
Embassy of the Tangerine Planet 🍊 (the planet that is one ellipse further from
the Sun than Earth's ellipse).

You are now officially certified to include "law_dictionary" in your practice!

Encore! Encore! Encore! Encore!

******


# law_dictionary

---

## description   
This module checks that dictionaries provided are legit.  

---		
		
## install
`[xonsh] pip install law_dictionary`

---

## tutorial
The "dictionary" passed to the "check" function might be modified.    
Therefore `dictionary_2 = copy.deepcopy (dictionary_1)` should be used
if you'd like the original `dictionary_1` to be preserved.    


### 101 
In this example, an obstacle is found because "directory_2" is not in the "laws"   
and "allow_extra_fields" is False.   

With "return_obstacle_if_not_legit" a report is returned instead of an exception   
being raised.  

```
import law_dictionary

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
	raise Exception (report ["obstacle"])	
```


### contigencies   
If "required" is False, then the "contingency" value is returned
or the value returned by a "contingency" function.

After "contingency" step, the "type" is checked,
if "type" is passed to the "laws".

```
import law_dictionary

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

# The consequence of this check is that there are no "obstacles"
# and the dictionary is modified to have this structure:
'''
{
	"directory_1": "/",
	"directory_2": "/drives"
}
'''
```


### allowance
The consequence of this check is that there are no "obstacles" or modifications
to either dictionary.

```
import law_dictionary

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
```


### multiple levels
There's not a tree structure possible for multiple levels,   
however after a level 1 check, level 2, etc. checks can    
be run.  

```
import law_dictionary

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
```