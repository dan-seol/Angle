import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup


header={
'authority': 'fls-na.amazon.ca',
'pragma': 'no-cache',
'cache-control': 'no-cache',
'dnt': '1',
'upgrade-insecure-requests': '1',
'accept-language': 'en-US,en;q=0.9',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'none',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54', 
}

cookie={
'session-id-time': '2082787201l', 
'ubid-acbca': '133-5040475-3032739',
'session-id': '143-4817918-8189165', 
'x-wl-uid': '1hNOllqEAuVBibHLc1MhQVPGFxaWsvfDbkrJVdXiu8WH5y6ElPH1dHZelCxilOsDZBBe958Xn7Fc=',
'i18n-prefs': 'CAD',
'session-token': 
'Kv/W8NI8bKf421mDVH7CKw3enRWKURruIyqXsZlzzYGNjn9B8azwYeHtx2hOqyDcm0ilJ84ORgKT8Qo3hjPUfAFwfplf6SJwS9JKIlrtkQz9IHo6I2HIqM7HMpHI8nYiNx+Cpbo30r8WNGiAUHJmzlqtPYsyMNyhvj6/ipsn114lzsM2NYeFQqI2dDz6XRO/',
}

logger = logging.getLogger("scraping")

logger.setLevel(logging.DEBUG)
if not len(logger.handlers):
    # create a file handler
    handler = logging.FileHandler(("scraping"+'.log'))
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the file handler to the logger
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())


def checkPageStatus(page):
    if page.status_code == 200:
        return page
    else:
        logger.info(str(page.status_code))
        return "Error with status code " + str(page.status_code)

def getAmazonSearch(search_query):
    url="https://www.amazon.ca/s?k=" + search_query
    logger.info("Here is the url address: %s"%url)
    page=requests.get(url, headers=header, cookies=cookie)
    return checkPageStatus(page)


def populateAsin(search_query):
    data_asin=[]
    response=getAmazonSearch(search_query)
    logger.info("Get search content")
    logger.info(response.content)
    soup=BeautifulSoup(response.content, features="lxml")
    for i in soup.findAll("div", {'class':"sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32" }):
        data_asin.append(i['data-asin'])
    logger.info("length of data_asin: " + str(len(data_asin)))
    return data_asin

def searchAsin(asin):
    url="https://www.amazon.ca/dp/"+asin
    logger.info("Here is the url address from the asin: %s"%url)
    page=requests.get(url, headers=header, cookies=cookie)
    return checkPageStatus(page)

def populateLinks(data_asin):
    links=[]
    for i in range(len(data_asin)):
        response=searchAsin(data_asin[i])
        logger.info("Link response content " + str(i))
        logger.info(response.content)
        soup=BeautifulSoup(response.content, features="lxml")
        for i in soup.findAll("a", {'data-hook':"see-all-reviews-link-foot"}):
            links.append(i['href'])
    logger.info("length of links: " + str(len(links)))
    return links

def searchReviews(review_link):
    url="https://www.amazon.ca"+review_link
    print("Here is the url address to the review link: %s"%url)
    page=requests.get(url, headers=header, cookies=cookie)
    return checkPageStatus(page)

def populateReviews(links):
    reviews=[]
    for j in range(len(links)):
        for k in range(100):
            response=searchReviews(links[j]+'&pageNumber='+str(k))
            logger.info("Review response content " + str(k))
            soup=BeautifulSoup(response.content, features="lxml")
            for i in soup.findAll("span", {'data-hook':"review-body"}):
                reviews.append(i.text)
    logger.info("length of reviews: " + str(len(reviews)))
    return reviews

def saveReviews(reviews):
    rev={'reviews': reviews}
    review_data=pd.DataFrame.from_dict(rev)
    review_data.to_csv("reviews_scraped.csv", index=False)


def main():
    TOOTHBRUSHES = "toothbrushes"
    saveReviews(populateReviews(populateLinks(populateAsin(TOOTHBRUSHES))))
    logging.shutdown()
main()

     
        

 
