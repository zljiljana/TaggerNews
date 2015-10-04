import sys
import alchemy.tags
import alchemy.parser

cache = None

if __name__ == "__main__":
	while True:
		if not cache:
			alchemy.tags.importModel()
		alchemy.parser.parse()
		print "Press enter to re-run the script', CTRL-C to exit"
		sys.stdin.readline()
		reload(alchemy.tags)
		reload(alchemy.parser)