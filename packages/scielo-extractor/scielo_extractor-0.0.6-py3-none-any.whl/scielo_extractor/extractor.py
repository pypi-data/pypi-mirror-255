import urllib
import lxml.html
import requests
import json
from tqdm import tqdm
from xylose.scielodocument import Article
import pandas as pd

class ScieloSearch:
  def __init__(self):
    self.base_uri = 'https://search.scielo.org/'
    self.page_size = 10
    self.total_papers_xpath = '/html/body/section/div/div/div[1]/div[1]/div[1]/strong'
    self.result_paper_item_xpath = '/html/body/section/div/div/div[1]/div[2]/div[3]/div'

  def query(self, query, params={'from': 0, 'page': 1}, result_size=5000, format=None, progress=False):
    total_papers = []
    params = {'q': query, **params}
    total = self.get_total_papers(query, params)
    if not total:
      return None

    if progress:
      pages = tqdm(range(1, total + 1, self.page_size))
    else:
      pages = range(1, total + 1, self.page_size)
    for page in pages:
      count_papers = len(total_papers)
      if count_papers >= result_size:
        break
      total_papers += self.get_papers_in_page(query, result_size, count_papers, params)
      params['page'] += page
      params['from'] += self.page_size
    if format:
      return self.format(total_papers, format=format)
    else:
      return total_papers

  def get_total_papers(self, query, params):
    encoded_query_params = urllib.parse.urlencode(params)
    request_url = f'{self.base_uri}?{encoded_query_params}'
    tree = self.send_request(request_url)
    if tree.xpath(self.total_papers_xpath):
      return int(tree.xpath(self.total_papers_xpath)[0].text.replace(' ', ''))

  def get_papers_in_page(self, query, result_size, count_papers, params):
    papers = []
    encoded_query_params = urllib.parse.urlencode(params)
    request_url = f'{self.base_uri}?{encoded_query_params}'
    tree = self.send_request(request_url).xpath(self.result_paper_item_xpath)
    for element in tree:
      if count_papers + len(papers) == result_size:
        break
      if 'id' not in element.attrib:
        continue
      scielo_id = '-'.join(element.attrib['id'].split('-')[0:2])
      article = self.get_scielo_paper(scielo_id)
      papers.append(article)
    return papers

  def send_request(self, request_url):
    response = requests.get(request_url)
    return lxml.html.fromstring(response.text)

  def get_scielo_paper_json(self, scielo_paper_id):
    article_json = json.loads(urllib.request.urlopen(f'http://articlemeta.scielo.org/api/v1/article/?code={scielo_paper_id}&format=json').read())
    return article_json

  def get_scielo_paper(self, scielo_paper_id):
    article_json = self.get_scielo_paper_json(scielo_paper_id)
    article = Article(article_json)
    return article

  def format(self, papers, format='json'):
    papers_list = []
    for paper in papers:
      paper_dict = {}
      authors_list = []
      try:
        for author in paper.authors:
          authors_list.append(author['surname'] + ',' + author['given_names'])
          paper_dict['authors'] = ';'.join(authors_list)
      except:
        paper_dict['authors'] = ''
      try:
        paper_dict['title'] = paper.original_title()
      except:
        paper_dict['title'] = ''
      try:
        paper_dict['journal'] = paper.journal.title
      except:
        paper_dict['journal'] = ''
      try:
        paper_dict['volume'] = paper.issue_label
      except:
        paper_dict['volume'] = ''
      try:
        paper_dict['issue'] = paper.issue()
      except:
        paper_dict['issue'] = ''
      try:
        paper_dict['doi'] = paper.doi
      except:
        paper_dict['doi'] = ''
      try:
        paper_dict['year'] = paper.publication_date if paper.publication_date else paper.ahead_publication_date
      except:
        paper_dict['year'] = ''
      try:
        paper_dict['abstract'] = paper.original_abstract()
      except:
        paper_dict['abstract'] = ''
      try:
        paper_dict['start_page'] = paper.start_page
      except:
        paper_dict['start_page'] = None
      try:
        paper_dict['end_page'] = paper.end_page
      except:
        paper_dict['start_page'] = None
      papers_list.append(paper_dict)
    if format == 'json':
      return json.dumps(papers_list, indent=4)
    elif format == 'dict':
      return papers_list
    elif format == 'dataframe':
      return pd.DataFrame(papers_list)
    else:
      raise Exception(f'format "{format}" not supported')
