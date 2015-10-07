# Tagger News 

Tagger News is an automatic tagging system for [Hacker News]. By generating tags for the articles it becomes easy to browse and search for documents or topics you are interested in. For this project Hacker News served as a data source, however, the pipeline is easily extendable to other news sources as long as there is a way to fetch the URLs of the articles. Below I will explain how auto-tagging works and how I approached this task.

### How does auto-tagging work?
Auto-tagging is a system which automatically assigns tags from a predefined set to a string of arbitrary length. When posed like this, auto-tagging sounds like a supervised multiclass classification problem. However, it is hard to find a training set of tagged articles that are relevant to your domain, and it's almost unfeasible to make one that is large enough to cover all the topics. That's why auto-tagging is considered to be an unsupervised problem.

There are two common approaches to this problem. One is to build a [topic model] on a training set of documents and then use this model to make predictions on new data. Topic model can end up with noisy terms that make your tagging system look bad. Another drawback of this approach (related to my task here) is that Hacker News articles cover aaaall the topics in the world so to make accurate predictions it would take a lot of HN scrapping.

Second approach is to find the "nearest neighbor" tag based on some textual or semantic similarity of an input to a predefined set of tags. This is the approach I took. Having the right similarity metric is the key to success in this approach. 

### How does Tagger News work?
[Tagger News] fetches the articles from Hacker News API and sends them through [AlchemyAPI] which returns the list of 15 most relevant keywords for each article. These keywords are then sent to my [word2vec] model that compares the keywords to a list of curated tags (coming from [Freebase]). Based on vector similarity word2vec model picks two most relevant tags that are finally rendered on the webpage. Word2Vec is trained on GoogleNews dataset and contains approx. 3 billion phrases. Finally, all the data related to an article is being saved to RethinkDB. Throughout the entire pipeline I used Python and Flask for the front-end.

<!-- As a little back story - Hacker News API graciously makes available the list of the 300 most popular articles at a given time and all the new items that users submit on to their website (comments, jobs, polls, etc.). I am only interested in items of type "story" (in other words, only articles). For each story I have the URL of the page but not the text of the article. This created problems for me due to the fact that HN articles are coming from various sources that made the web scraping a hard problem. For that reason my next step in the pipeline was to submit a URL of the article to AlchemyAPI that returns the keywords based on the content of the text. 
-->


[hacker news]: <https://news.ycombinator.com/>
[topic model]: <http://journalofdigitalhumanities.org/2-1/topic-modeling-a-basic-introduction-by-megan-r-brett/>
[Tagger News]: <http://www.taggernews.xyz/>
[word2vec]: <https://code.google.com/p/word2vec/>
[Freebase]: <http://www.freebase.com/>
[AlchemyAPI]: <http://www.alchemyapi.com/>