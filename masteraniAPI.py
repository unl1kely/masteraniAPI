from bs4 import BeautifulSoup as bs
from JskPy import encodeUrl, best_match
from requests import get


##############
domainMasterani = "https://www.masterani.one"
animeServers = "https://gogo-play.net/"

class Anime:
	def __init__(self, title):
		self.kind=list
		self.title = title
		self.search_url = "{0}/search?q={1}".format(domainMasterani, encodeUrl(self.title))
		self.search_response = get(self.search_url)
		if not "200" in str(self.search_response):
			self.message = "Unexpected network error."
			self.found = 0
		else:
			self.search_soup = bs(self.search_response.text, "html.parser")
			self.result_div = self.search_soup.find(class_="movie-container")
			self.result_list = self.result_div.find_all("h3")
			if len(self.result_list)==0:
				self.found = 0
				self.message = "{0} - Anime not found.".format(self.title)
			else:
				self.titles = [a_tag.find("a").string for a_tag in self.result_list]
				self.result_index = best_match(self.title, self.titles)
				if self.result_index!=None:
					self.found = 1
					self.name = self.titles[self.result_index]
					self.title_link = self.result_list[self.result_index].find("a").get("href")
					self.message = "Found anime : "+self.name
				else:
					self.found = 0
					self.message = "{0} - Anime not found.".format(self.title)
	def watch(self, season, episode, quality="Auto", launch=True):
		season = int(season)
		ep = int(episode)
		self.title_response = get(self.title_link)
		self.title_soup = bs(self.title_response.text, "html.parser")
		season_div = self.title_soup.find_all(class_="season")[-season]
		eps = season_div.find_all(class_="btn-inline")[1:]
		ep_link = eps[-ep].get("href")
		ep_response = get(ep_link)
		ep_soup = bs(ep_response.text, "html.parser")
		iframe_link = ep_soup.find("iframe").get("src")
		iframe_response = get(iframe_link)
		if not "200" in str(iframe_response):
			self.message = "Unexpected network error."
			self.found = 0
		else:
			iframe_soup = bs(iframe_response.text, "html.parser")
			self.video_id = iframe_soup.find("input").get("value")
			self.watch_link = "{0}loadserver.php?id={1}".format(animeServers, self.video_id)
			self.found = 1
			if __name__ != '__main__':
				self.message = f"{self.name} S{season}E{ep} video link copied to clipboard"
			else:
				self.message = self.watch_link
		if self.found==1:
			if launch==True:
				try:
					import webbrowser
					webbrowser.open(self.watch_link)
				except Exception as e:
					print("{0}\nCould not go to watch link.".format(e))
		return self.message
	def download(self, season, episode, quality="720p", launch=True):
		# class properties
		season = int(season)
		ep = int(episode)
		download_quality = quality
		if download_quality=="Auto":
			download_quality = "720p"
		# anime main page
		self.title_response = get(self.title_link)
		self.title_soup = bs(self.title_response.text, "html.parser")
		# get season
		try:
			season_div = self.title_soup.find_all(class_="season")[-season]
		except IndexError:
			self.found = 0
			self.message = "No season {0} found for {1}".format(season, self.name)
			return self.message
		# get episode
		eps = season_div.find_all(class_="btn-inline")[1:]
		try:
			ep_link = eps[-ep].get("href")
		except IndexError:
			self.found = 0
			self.message = "No episode {0} in season {1} of {2}".format(ep, season, self.name)
			return self.message
		ep_response = get(ep_link)
		ep_soup = bs(ep_response.text, "html.parser")
		iframe_link = ep_soup.find("iframe").get("src")
		print(iframe_link)
		iframe_response = get(iframe_link)
		if not "200" in str(iframe_response):
			self.message = "Unexpected network error."
			self.found = 0
			return self.message
		iframe_soup = bs(iframe_response.text, "html.parser")
		# download menu
		self.video_id = iframe_soup.find("input").get("value")
		download_page = "{0}download?id={1}".format(animeServers, self.video_id)
		download_response = get(download_page)
		if not "200" in str(download_response):
			self.message = "Unexpected network error."
			self.found = 0
			return self.message
		download_soup = bs(download_response.text, "html.parser")
		download_tags = download_soup.find_all(class_="dowload")
		links = dict()
		for div in download_tags:
			a = div.find("a")
			a_text = a.string
			if "Download " in a_text:
				break
			a_name = a_text[a_text.index("(")+1:a_text.index(" - ")]
			a_link = a.get("href")
			links[a_name] = a_link
		self.download_link = False
		# quality pick
		for name in links:
			if str(download_quality).lower() in name.lower():
				self.download_link = links[name]
				break
		if not self.download_link:
			found_qualities = tuple(q for q in links)
			self.TryWith = str(found_qualities)
			for char in ["'",'"',"(",")"]:
				self.TryWith = self.TryWith.replace(char, '')
			self.message = "{0} not available for this episode. Try with {1}.".format(download_quality, self.TryWith)
			self.found = 0
		else:
			if __name__ != '__main__': # imported 
				self.message = "{0} S{1}E{2} download link copied to clipboard".format(self.name, season, ep)
			else:
				self.message = self.download_link
			self.found = 1
		return self.message
#
