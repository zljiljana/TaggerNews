#!/usr/bin/python

import alchemy.tags
import alchemy.parser

if __name__ == "__main__":
	if alchemy.tags.importModel():
		alchemy.parser.parse()
	else:
		print "do not update anything. Limit reached."

	print "Page updated"
