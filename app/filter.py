import rethinkdb as r
import os

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

connection = r.connect(host=RDB_HOST, port=RDB_PORT)

# Define a function that will return an HTML snippet.
def filter(userTag):
    print userTag
    # need to get the 
    res = ""
    try:
        myDict = list(r.db("test").table("tag_dict").pluck(userTag).run(connection))[0][userTag]
        if (myDict): # if it exists
            # join the elements in a list 
            res = ' '.join(myDict)
    except KeyError:
        res = "<td text-align=\"right\" valign=\"top\">Sorry, no results for tag: " + userTag + "</td>"

    # Return the snippet we want to place in our page.
    return res