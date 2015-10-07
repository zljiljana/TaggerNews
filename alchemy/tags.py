import sys
import gensim, math, numpy
import unicodedata, os
from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()

topLvlTags = ['media','people','business','biology','sport','education','architecture','government','medicine','gaming',
	'geography','astronomy','military','aviation','food','chemistry','law','religion', 'travel', 'theater', 'celebrity',
	'film', 'performance', 'computer hardware','music','computer software', 'digicatal_camera','engineering','fashion','physics', 'animals', 'fiction', 'literature',
	'gadgets', 'history','robotics', 'invention', 'automotive','hobby'] # list of top level tags

tagMap = {'media': ['e_commerce','brand','status','royalty','publication','review','author','writer','actor','album','artist','genre','instrument','festival', 'marriage','friendship','romantic_relationship','rehab'],
	'business': ['work balance','executive_commitee','culture','us_economy','interview','scandal','privacy','insurance','security', 
		'apple','amazon', 'facebook', 'netflix','twitter','venture capital','asset', 'currency', 'stock_exchange', 'investment', 'sponsorship', 'shareholder', 'organization', 'non_profit_organization', 'acquisition', 'leadership', 'startup', 'founder'],
	'biology': ['protein','chromosome','animal_breed','gene','amino_acid'],
	'sports': ['sports_team','football','basketball','soccer','championship'],
	'education': ['research','scholarly_work','school_district','university','dissertation','academia'],
	'performance': ['orchestra','concert','album', 'art','disaster','exhibition','conference','award'],
	'architecture': ['skyscraper','house','building','tower','museum','architectural_style'],
	'government': ['minister','legislature','president','agency','election','campaign', 'citizenship'],
	'medicine': ['virus','infection','cancer','brain','nerve','symptom','drug','physician','drug brand', 'hospital', 'disease'], 
	'gaming': ['entertainment','videogame','mobile','games','game series','game version'],
	'geography': ['continent', 'country','mountain','waterfall','glacier','river','lake','island'],
	'astronomy': ['cosmology','star','constellation','planet','asteroid','meteor_shower','galaxy','comet'],
	'military':['armed force','conflict','casualties','war'],
	'aviation':['airline','airport','plane crash','space','rocket','rocket_fuel','space_agency','satellite','spacecraft'],
	'food':['beer','tea','beverage','dish','restaurant','chef','cuisine','diet','recipe'],
	'travel':['destination','attraction','accommodation'],
	'computer hardware': ['graphics','kernel','screen','cpu','sensor','smartwatch','ebooks','smartphone','devices','interface','phone','processor','product_line',
		'electronics','protocol','format','web_browser','emulator','peripheral'],
	'computer software': ['audio', 'video','data science', 'computer_server','data_center','mobile_app','personal data','mathematics','scalability','open_source', 
		'object_oriented','algorithm', 'computer virus','operating_systems','encryption','malware','security alert','app_store', 'ios', 'programming_language',
		'linux', 'unix', 'mechanical_engineeros', 'windows','lua','security_flaw','wifi','automaton','web','neural_networks','html', 'big data', 'virtualization','license',
		'computing_platform','simulator','crowdsourcing', 'certificate', 'integration','database', 'java','javascript', 'sdk','data','artificial_intelligence',
		'data_storage','open_source','android','grammar','paradigm', 'software_provider','compatibility','proprietary_data','email','bitcoin', 'digital_content','analytics','predictive_analytics',
		'statistical_data','statistical_methods','mathematical_model','cloud_computing','python', 'c', 
		'deep learning','language_processing','cloudera','aws','kafka','random forest','scala', 'plugin','spark', 'hadoop','sql', 'stack overflow', 'text editor','latex', 'lisp',
		'software architecture','compilers','syntax','website','blog','internet_provider','internet_protocol','api','computer_servers','internet_traffic','social_network',
		'file_sharing', 'copyrights'],
	'chemistry':['chemical_compound','molecule'],
	'law':['protocol','patent','legal case','court','judge', 'law_enforcement'],
	'religion':['belief','religious leader','religious organization'],
	'automotive':['environment','fuel','car body','car company','car designer','car model','transmission', 'car engine','emissions','driving','biking' ,'healthy_life'],
	'hobby':['collector','collection'],
	'digital_camera':['camera format','camera resolution', 'image_processing'],
	'engineering':['machine_learning','bioengineering','bioinformatics', 'nanotechnology','neuroscience','aerospace_engineering','energy','power plants','oil','engineering_firm','civil_engineer', 'mechanical_engineer', 'chemical_engineer', 'battery','engine'],
	'fashion':['garment','home decor'],
	'physics':['calculus','scientific method','dynamics','quantum_theory','optimization', 'theoretical_physics','quark', 'particle','measurement unit']}

# 'automotive' or 'emissions' or 'car company' or 'car model' or 'car engine' or 'environment' or 'scandal'


def __init__(self):
	# Open the key file and read the key
	f = open("api_key.txt", "r")
	key = f.read().strip()
	print key

	if key == '':
	    # The key file should't be blank
	    print(
	        'The api_key.txt file appears to be blank, please run: python alchemyapi.py YOUR_KEY_HERE')
	    print(
	        'If you do not have an API Key from AlchemyAPI, please register for one at: http://www.alchemyapi.com/api/register.html')
	    sys.exit(0)
	elif len(key) != 40:
	    # Keys should be exactly 40 characters long
	    print(
	        'It appears that the key in api_key.txt is invalid. Please make sure the file only includes the API key, and it is the correct one.')
	    sys.exit(0)
	else:
	    # setup the key
	    self.apikey = key

	# Close file
	f.close()

def importModel():
	print "Loading Word2Vec model ..."
	dir = os.path.dirname(__file__)
	path = os.path.join(dir, 'vectors-phrase.bin')
	global model
	model = gensim.models.Word2Vec.load_word2vec_format(path, binary=True)
	print "Word2Vec loaded."
	test_url = "https://en.wikipedia.org/wiki/Main_Page"
	if (getKeywords(test_url) == 'limit-exceeded'):
		return False
	return True

def getKeywords(url):
	# call alchemyAPI keyword extractor
	response = alchemyapi.keywords('url', url)
	# placeholder for keywords
	kw = []
	if response['status'] == 'OK':
		#print('## Response Object ##')
		#print(json.dumps(response', indent=4))
		try:
			for keyword in response['keywords']:
				s = unicodedata.normalize('NFKD', keyword['text']).encode('ascii','ignore')
				kw.append(s.lower())
				# return only first 15 keywords
				if len(kw) == 15:
					return kw
		except KeyError:
			pass
	else:
		print('Error in keyword extaction call: ', response['statusInfo'])
		# there are 2 special cases I want to track: daily limit and page not html
		if response['statusInfo'] == 'daily-transaction-limit-exceeded':
			return ['limit-exceeded']
		if response['statusInfo'] == 'page-is-not-html':
			return ['page-is-not-html']
		# otherwise return a generic message
		return ['keywords-not-found']

	# return top 15 keywords (ordered by relevance)
	return kw[:15]


def getTags(keywords):
	allTags = topLvlTags+tagMap['media']+tagMap['business']+tagMap['biology']+tagMap['sports']+tagMap['education']+tagMap['performance']+tagMap['architecture']+\
		tagMap['government']+tagMap['medicine']+tagMap['gaming']+tagMap['geography']+tagMap['astronomy']+tagMap['military']+tagMap['aviation']+tagMap['food']+tagMap['travel']+\
		tagMap['computer software']+tagMap['computer hardware']+tagMap['engineering']+tagMap['chemistry']+tagMap['law']+tagMap['religion']+tagMap['automotive']+\
		tagMap['digital_camera']+tagMap['hobby']+tagMap['fashion']+tagMap['physics']
	max1cos = 0.0
	max2cos = 0.0
	tag1 = allTags[0]
	tag2 = allTags[1]
	for tag in allTags:
		cosine = 0
		for keyword in keywords:
			try:
				k = keyword.split()
				t = tag.split()
				cosine += model.n_similarity(t, k)
			except KeyError:
				pass
		# if current cosine bigger than the lower of the two max cosine similarities
		if (isinstance(cosine, numpy.float64)):
			if (cosine > max2cos):
				# if bigger than the biggest too
				if (cosine>max1cos):
					max2cos = max1cos
					tag2 = tag1
					max1cos = cosine
					tag1 = tag
				# if bigger than the second biggest only change that one
				else:
					max2cos = cosine
					tag2 = tag

	return [tag1, tag2]


if __name__ == '__main__':
	importModel()
	test_url = 'http://www.nytimes.com/2015/09/20/magazine/barbie-wants-to-get-to-know-your-child.html?hp&action=click&pgtype=Homepage&module=photo-spot-region&region=top-news&WT.nav=top-news'
	myTags = getTags(getKeywords(test_url))
	print ('')
	print ('')
	print "Selected tags: ", myTags
