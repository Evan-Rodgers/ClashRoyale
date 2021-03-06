# === Tools for receiving data about the Clash Royale universe ===

import meta_handling as mh

import requests
from bs4 import BeautifulSoup

from PIL import Image

# retrieves deck usage data
def get_decks(url, save_imgs=False):
    """
    :param save_imgs: scrape and save all card images to a folder
    :param url: page containing HTMl deck data
    :return collection: a list containing a list for each deck used
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    decksUsed = soup.findAll("div", {"class": "recentWinners__decklist"})
    # timeStamps = soup.findAll("div", {"class": "ui__smallText ui__greyText"})
    # times = [str(ts.contents[0]) for ts in timeStamps]

    collection = []

    for deck in decksUsed:

        allCards = deck.findChildren('a', recursive=False)
        deckSet = []

        for card in allCards:
            # format card names
            cardString = card.get('href').split('card/')[1]
            cardString = cardString.replace('+', '').replace('-', '').replace('.', '')
            deckSet.append(cardString)

            if save_imgs:
                # path to card image
                img_path = card.contents[1].get('src')
                img = Image.open(requests.get(img_path, stream=True).raw)
                save_image(img, cardString)

        collection.append(deckSet)

    return collection


# saves card images to a folder
def save_image(image, card_str):
    """
    :param image: the PIL Image object
    :param card_str: name of the card
    :return: None
    """
    path = 'C:/Users/Matt/PycharmProjects/ClashRoyale/images/'
    filename = card_str+'.png'
    # If the file already exists, who cares? Just re-save it
    image.save(path+filename)
    print('Image of '+card_str+' saved!')


# update edges between nodes in a deck
def push_deck(deck, graph):
    """
    :param graph: parent networkx graph object to be updated
    :param deck: a list containing a string for each of the 8 cards
    :return: None
    """
    # Increment the weight for each association
    for card in deck:
        # relatedCards = deck.remove(card)
        relatedCards = [c for c in deck if c != card]
        for eachCard in relatedCards:

            # Networkx implementation:

            # Perhaps each deck is a sub-graph that's pushed to the parent
            if graph.has_edge(card, eachCard):
                graph[card][eachCard]['usages'] += 1
            else:
                graph.add_edge(card, eachCard, usages=1)

# creates a new network graph from recent data
def build_graph(decks=None, Top200=True):

    # create an empty graph network with all assigned node attributes
    if decks is None:
        return mh.create_empty_graph()
    else:
        G = mh.create_empty_graph()
        n = 0

    # Ugly
    if Top200:
        url = 'https://statsroyale.com/decks/challenge-winners?type=top200&page='
    else:
        url = 'https://statsroyale.com/decks/challenge-winners?type=grand&page='

    page = 1
    while n < decks:

        url = url + str(page)
        for deck in get_decks(url, save_imgs=False):
            n += 1
            push_deck(deck, G)
        page += 1
    print(f"Decks Used: {n}")
    return G

