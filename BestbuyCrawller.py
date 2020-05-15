import requests
from bs4 import BeautifulSoup
import re


# this function takes in parameters and return new waitingList and crawledlinks
def getSubLinks(domainurl, suburls, waitingList, crawledlinks):
    if(len(suburls) != 0): # check if the suburls is empty
        crawledlinks.append(suburls)
    newpage = requests.get(domainurl + suburls)
    newdata = newpage.text
    newsoup = BeautifulSoup(newdata, features="html.parser")
    print("Title of page: "+newsoup.head.title.string)  # this is sub url's page title

    # for eachLink link inside the waitingList, find sub-links on that page
    for sub in newsoup.find_all('a', attrs={'href': re.compile("^/en-ca/")}):
        sub_url = sub.get('href')
        # check to avoid duplicated urls in waitingList and crawledLinks lists
        if (sub_url not in waitingList and sub_url not in crawledlinks):
            if (re.search('^/en-ca/product/*', sub_url)):
                crawledlinks = getProduct(domainUrl, sub_url, crawledlinks)
                crawledlinks = list(dict.fromkeys(crawledlinks)) # avoid duplicated urls
            else:
                waitingList.append(sub_url)
    waitingList = list(dict.fromkeys(waitingList))  # avoid duplicated urls
    return (waitingList, crawledlinks)


# this function takes in parameters and return a new crawledlinks
def getProduct(domainurl, productUrl, crawledlinks):
    tab = '\t'
    if(productUrl in crawledlinks):
        return
    crawledlinks.append(productUrl)
    productpage = requests.get(domainurl + productUrl)
    productdata = productpage.text
    productsoup = BeautifulSoup(productdata, features="html.parser")
    print(tab + "Title of product page: " + productsoup.head.title.string)
    category = productsoup.find_all('span', attrs={'class': 'x-crumb', 'property': 'name'})
    if (category is not None):
        space=' '
        for x in range(1, len(category) - 1):
            print(tab+space*x + category[x].string)
    productname = productsoup.find('h1', attrs={'class': 'productName_19xJx', 'itemprop': 'name'})
    if(productname is not None):
        print(tab*2 + "Product name: " + productname.string)

    webcode = productsoup.find('span', attrs={'itemprop': 'sku'})
    if (webcode is not None):
        print(tab*3 + "Web code: " + webcode.string)
    mode = productsoup.find('span', attrs={'itemprop': 'model'})
    if (mode is not None):
        print(tab*3 + "Model number: "+mode.string)
    print(tab*3 + "Url: " + productUrl)
    return crawledlinks


# this function sets limited numbers of links to crawl.
# This is used because crawling the entire site takes too long and will get time out exception
# You can define how many links you want to crawl for category or brand by setting numCategoryLinksToCrawl and numBrandLinksToCrawl
def limitCrawlLinks(waitingList, numBrandLink, numCategoryLink, numBrandLinksToCrawl, numCategoryLinksToCrawl, toCrawlList):
    # this loop add links form the waitingList to the toCrawlList
    for link in waitingList:
        if(re.search('^/en-ca/brand/*', link)):
            if numBrandLink < numBrandLinksToCrawl:
                toCrawlList.append(link)
                numBrandLink = numBrandLink + 1
        if re.search('^/en-ca/category/*', link):
            if numCategoryLink < numCategoryLinksToCrawl:
                toCrawlList.append(link)
                numCategoryLink = numCategoryLink + 1
        if numCategoryLink == numCategoryLinksToCrawl and numBrandLink == numBrandLinksToCrawl:
            return toCrawlList


# main program
domainUrl = "https://www.bestbuy.ca/"
waitingList = []
crawledLinks = []
# set crawler depth of pages. 1 means on home page, 2 means a sub page of the home page. 0 means not crawling any page
# i.e if depth = 2, it will crawl the home page and the home page's sub-pages
# every time depth +1, it goes down to a sub page of the current page
depth = 2

# the first crawling crawls the domain urls and get all links on it
# the program prints product info of the product link and add the url in a crawledLinks list
# for other urls, it will add in the allLinks list for future crawling
waitingList_and_crawledUrls = getSubLinks(domainUrl, "", waitingList, crawledLinks)
waitingList = waitingList_and_crawledUrls[0]
crawledLinks = waitingList_and_crawledUrls[1]
depth = depth-1
toCrawlList = [] # this list variable stores limited urls to crawl
numBrandLink = 0 # number of brand links
numCategoryLink = 0 # number of category links
numBrandLinksToCrawl = 3 # this variable set numbers of total links that can be added in toCrawledList
numCategoryLinksToCrawl = 3 # this variable set numbers of total links that can be added in toCrawledList

toCrawlList = limitCrawlLinks(waitingList, numBrandLink, numCategoryLink, numBrandLinksToCrawl, numCategoryLinksToCrawl, toCrawlList)

# in the following loop:
# for every url in the toCrawlList, it will print all product links and add them into crawledLinks
# for none product links, it will update waitingList and rerun the loop
while(depth>0):
    # each time loop eachLink in toCrawlList, have a variable to get the depth of current sub link
    for eachLink in toCrawlList:
        if(eachLink not in crawledLinks):
            if(re.search('^/en-ca/product/*', eachLink)):
                crawledLinks = getProduct(domainUrl, eachLink, crawledLinks)
            else:
                subDepth = depth
                # ensure every sub-link in the toCrawlList will crawl the depth as expected
                while(subDepth>0):
                    waitingList_and_crawledUrls = getSubLinks(domainUrl, eachLink, waitingList, crawledLinks)
                    subDepth = subDepth-1
                    waitingList = waitingList_and_crawledUrls[0]
                    crawledLinks = (waitingList_and_crawledUrls[1])
    depth = depth-1 # renew depth after crawling all sub-links
