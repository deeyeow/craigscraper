import time
import requests
from bs4 import BeautifulSoup

import notify


MINUTES_IN_SECOND = 0.017
MINUTES_IN_DAY = 1440


def main():

    # main menu
    print('\nWelcome to the Craigscraper')
    print('-------------------------------')
    print('1) Quickfind')
    print('2) Custom Search')
    print('3) Monitor Quickfind')

    userinput = input()
    while not userinput.isdigit() or int(userinput) < 1 or int(userinput) > 3:
        print('Incorrect query')
        userinput = input()

    # quickfind menu
    if int(userinput) == 1:

        item_list = get_itemlist()

        print('\nQuickfind menu')
        print('------------------')
        for i in range(len(item_list)):
            print(str(i + 1) + ') ' + item_list[i])

        # quickfind selection
        userinput = input()
        while not userinput.isdigit() or int(userinput) < 1 or int(userinput) > len(item_list):
            print('Incorrect query')
            userinput = str(input())

        search = item_list[int(userinput) - 1]

        thresholds = get_threshold(search)
        scrape_cg(search, thresholds)

    # custom search menu
    elif int(userinput) == 2:
        print('Search query: ')
        search = str(input()).lower().replace(' ', '+')
        print('\n')

        scrape_cg(search)

    # continuously monitor
    elif int(userinput) == 3:

        item_list = get_itemlist()
        items = ''
        for i in range(len(item_list)):
            items = items + item_list[i] + ' | '
        items = items[:-3]

        print('\nProducts to monitor:\n', items, '\n')
        print('Update every X minutes:')
        minutes = input()

        # limit updates to every 1 min - 1 day
        while not isfloat(minutes) or float(minutes) < MINUTES_IN_SECOND or float(minutes) > MINUTES_IN_DAY:
            if not isfloat(minutes):
                print('Incorrect query')
                minutes = input()
            elif float(minutes) < MINUTES_IN_SECOND:
                print('Minimum 1 second (0.017 minutes)')
                minutes = input()
            elif float(minutes) > MINUTES_IN_DAY:
                print('Maximum 1 day (1440 minutes)')
                minutes = input()

        seconds = float(minutes) * 60
        time_counter = 0

        thresholds = get_threshold('Razer Blade 15')
        price_lo = 1000

        # monitor until found below certain price
        while True:
            names_found, prices_found, links_found = scrape_cg('Razer Blade 15', thresholds, price_lo)
            if names_found[0] != 'None':
                print('Time elapsed:', time_counter * seconds / 60, 'minutes, or', time_counter * seconds, 'seconds')
                print('Found ', len(names_found), 'items under $' + str(price_lo) + ', emailing user...')
                notify.notify_user(names_found, prices_found, links_found, price_lo)
                break
            print('Time elapsed:', time_counter * seconds / 60, 'minutes, or', time_counter * seconds, 'seconds')
            time_counter = time_counter + 1
            time.sleep(seconds)





def isfloat(value):
    '''Returns if a string can be represented as float'''

    try:
        float(value)
        return True
    except ValueError:
        return False



def get_itemlist():
    '''Returns a list of items from file'''

    item_list = []
    with open ('data/thresholds.txt') as f:
        for line in f:
            if not line.rstrip().isdigit() and not line == '\n':
                item_list.append(line.rstrip())
    return item_list



def get_threshold(search):
    '''Returns thresholds from file given search query'''

    with open ('data/thresholds.txt') as f:
        for line in f:
            if search in line:
                threshold_lo = int(f.readline())
                threshold_hi = int(f.readline())
                break
    return threshold_lo, threshold_hi



def scrape_cg(search, thresholds=(float('-inf'), float('inf')), price_lo=(float('-inf'))):
    '''Prints all items matching search query and thresholds'''

    # initialize lists
    prices, price_ints, names, links, badwords = [], [], [], [], []
    names_found, prices_found, links_found = [], [], []
    notify_user = False

    # get bad words
    f = open('data/avoid_keywords.txt')
    for line in f:
        badwords.append(line.strip())
    f.close()

    # number of pages to scrape
    num_pages = 1
    num_items = 0

    for i in range(num_pages):

        if i > 0:
            pgnum = 's=' + str(i * 120) + '&'
        else:
            pgnum = ''

        URL = 'https://losangeles.craigslist.org/search/sss?query='
        #search = 'razer+blade+15'
        sortby = '&sort=rel'
        page = requests.get(URL + pgnum + search + sortby)

        # get soup
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all('li', {'class': 'result-row'})


        for result in results:

            # price of individual post
            price = result.find('span', {'class': 'result-meta'}).find('span', {'class': 'result-price'}).get_text()

            # strint to int
            if len(price) == 1: continue
            price_int = int(price.replace(',','')[1:])

            # filter by threshold
            if price_int < thresholds[0] or price_int > thresholds[1]: continue

            # name
            name = result.find('h3', {'class': 'result-heading'}).find('a').get_text()
            if len(name) == 0: continue
            
            # filter by bad words
            if any(badkw in name.lower() for badkw in badwords): continue
            
            # link
            link = result.find('a').get('href')
            if len(link) <= 0: continue

            # add result to list
            names.append(name)
            prices.append(price)
            price_ints.append(price_int)
            links.append(link)

            if price_int < price_lo:
                names_found.append(name)
                prices_found.append(price)
                links_found.append(link)
                notify_user = True

            num_items = num_items + 1

    # dont print in monitor mode
    if price_lo < -1:
        print('\n')
        for i in range(len(prices)):
            print(names[i])
            print(prices[i])
            print(links[i])
            print('------------------------')
        print('Threshold:', thresholds[0], 'to', thresholds[1])
        print('Total items:', num_items, '\n')

    # return items if found, otherwise return something meaningless
    if notify_user is True:
        return names_found, prices_found, links_found
    else:
        return (['None'], ['0'], ['None'])



if __name__ == '__main__':
    main()