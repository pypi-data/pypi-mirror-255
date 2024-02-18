




from .group import clique as clique_group

def clique ():
	import click
	@click.group ()
	def group ():
		pass

	import click
	@click.command ("example")
	def example_command ():	
		print ("example")

	group.add_command (example_command)

	group.add_command (clique_group ())
	group ()




#
