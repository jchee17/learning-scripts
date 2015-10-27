# Author: Matt Bonakdarpour
# Date: 2015-10-14
# Description: grab metadata for list of arxiv IDs
import csv
import numpy as np
import feedparser
import urllib
import re
import time
import sys


# constants
BATCH_SIZE = 500

# get list of IDs
docID_lst = []
with open('/home/mbonakda/hopper/demacro/full-corpus.txt') as f:
  reader = csv.reader(f, delimiter=' ')
  for docID,filename in reader:
    docID_lst.append(docID)

# batch them for bandwidth-limited download from arXiv API
docID_batch =[ docID_lst[ x:x+BATCH_SIZE ]  for x in xrange(0, len(docID_lst), BATCH_SIZE)]

# batched queries
feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
for batch_num in range(len(docID_batch)):
  batch    = docID_batch[batch_num]
  query    = 'http://export.arxiv.org/api/query?id_list=' + \
            ','.join(batch) + '&max_results=' + str(BATCH_SIZE);
  response = urllib.urlopen(query).read()
  feed     = feedparser.parse(response)
  for docIdx in range(len(feed.entries)):
    entry       = feed.entries[docIdx]

    paper_docID = batch[docIdx]

    paper_title  = entry.title.replace('\n', ' ')
    paper_title = re.sub(r'\s+', ' ', paper_title)
    paper_title = paper_title.encode('utf8')

    paper_subcategory = entry.tags[0]['term']
    paper_subcategory = paper_subcategory.encode('utf8')
    paper_category    = re.search(r"([^\.]*)\.?", paper_subcategory).group(1)

    paper_authors  = [re.sub(r'\s+', ' ', x['name']).encode('utf-8') for x in entry.authors]

    # print for metadata file
    suffix = ''
    if(len(paper_authors) > 2):
      suffix = ', ...'
      authors = ', '.join(paper_authors[:2]) + suffix
    print "{}\t {}\t {}\t {}".format(paper_docID,paper_title,authors,paper_category)
  pct = '%.4f' % round((batch_num+1)/float(len(docID_batch)), 1)
  sys.stderr.write(str(batch_num+1) + ' out of ' + str(len(docID_batch)) + '\n')
  time.sleep(3)

