import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # Ensure this comes after setting the backend
import warnings

def chunk_game_ids(ids, chunk_size=20):
    return [ids[i:i + chunk_size] for i in range(0, len(ids), chunk_size)]

#################################################################################
def get_collection(name, base_url):
    df = pd.DataFrame()
    username_param = 'username=' + name
    owned_param = 'own=1'
    url = base_url + 'collection?' + username_param + '&' + owned_param

    response = requests.get(url)
    # If the response status code is 202 (vs. 200) then it indicates BGG has queued your request
    # and you need to keep retrying (hopefully w/some delay between tries) until the status is not 202.
    while response.status_code == 202:
        time.sleep(5)
        response = requests.get(url)
    if response.status_code != 200:
        print(f"Collection Error: {response.status_code}, {response.text}")

    # parse xml and get ids for all games in the collection
    root = BeautifulSoup(response.content, 'xml')
    game_ids = [item.get('objectid') for item in root.find_all('item')]

    # group game_ids into 20 item chunks
    game_id_chunks = chunk_game_ids(game_ids)

    # for each chunk, get details if stats are available
    for chunk in game_id_chunks:
        details_url = base_url + 'thing?id=' + ','.join(chunk) + '&stats=1'
        details_response = requests.get(details_url)

        if details_response.status_code != 200:
            print(f"Details Error: {details_response.status_code}, {details_response.text}")
            break  # don't move on to the next chunk if there's an error as we dont want a partial collection

        details_root = BeautifulSoup(details_response.content, 'xml')

        for item in details_root.find_all('item'):
            name = item.find('name', attrs={'type': 'primary'}).get('value')
            year = item.find('yearpublished').get('value')
            stats = item.find('statistics')
            rating = stats.find('ratings')if stats else None
            users_rated = rating.find('usersrated').get('value') if rating and rating.find('usersrated') else None
            avg_rating = rating.find('average').get('value') if rating and rating.find('average') else None
            publisher = item.find('boardgamepublisher').get('value') if item.find('boardgamepublisher') else None

            row = {'name': name, 'year': year, 'publisher': publisher, 'users_rated': users_rated, 'avgrating': avg_rating}

            # get different category tags on each game
            categories = item.find_all('link', attrs={'type': 'boardgamecategory'})
            row['categories'] = ', '.join(category['value'] for category in categories if category.has_attr('value'))

            # get different mechanics tags on each game
            mechanics = item.find_all('link', attrs={'type': 'boardgamemechanic'})
            row['mechanics'] = ', '.join(mechanic['value'] for mechanic in mechanics if mechanic.has_attr('value'))

            # get different rankings for each game
            ranks = rating.find('ranks').find_all('rank') if rating and rating.find('ranks') else []
            for rank in ranks:
                rank_name = rank.get('friendlyname')
                value = rank.get('value')
                row[rank_name] = value

            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        time.sleep(5)  # be nice to the server

    return df
#################################################################################
def clean_data(df):
    # convert "Not Ranked" and Nan to None
    df = df.replace('Not Ranked', None)
    df = df.replace('Nan', None)

    # convert to numeric
    df['users_rated'] = pd.to_numeric(df['users_rated'])
    df['avgrating'] = pd.to_numeric(df['avgrating'])
    # df['min players'] = pd.to_numeric(df['min players'])
    # df['max players'] = pd.to_numeric(df['max players'])

    # unique list of categories
    categories = df['categories'].str.split(', ').explode().unique()
    mechanics = df['mechanics'].str.split(', ').explode().unique()

    # create a column for each category and mechanic and add flag if the game is in that category
    for category in categories:
        df['Category: ' + category] = df['categories'].str.contains(category)
    for mechanic in mechanics:
        df['Mechanic: ' + mechanic] = df['mechanics'].str.contains(mechanic)

    # drop categories and mechanics columns
    df = df.drop(columns=['categories', 'mechanics'])

    return df

#################################################################################
def get_plays(name, base_url):
    df = pd.DataFrame()
    username_param = 'username=' + name
    type_param = 'thing'
    url = base_url + 'plays?' + username_param + '&' + type_param

    response = requests.get(url)
    if response.status_code != 202:
        print(f"Plays Error: {response.status_code}, {response.text}")

    root = BeautifulSoup(response.content, 'xml')

    for play in root.find_all('play'):
        date = play.get('date')
        item = play.find('item')
        name = item.get('name')
        row = {'game': name, 'date': date}

        players = play.find('players').find_all('player') if play and play.find('players') else []
        for player in players:
            row['player'] = player.get('name')
            row['winner'] = row['player'] if player.get('win') == '1' else None

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    return df
#################################################################################
def get_hot_list(base_url):
    df = pd.DataFrame()
    type_param = 'type=boardgame'
    url=base_url + 'hot?' + type_param

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Hot List Error: {response.status_code}, {response.text}")

    root = BeautifulSoup(response.content, 'xml')

    for item in root.find_all('item'):
        name = item.find('name').get('value')
        rank = item.get('rank')
        row = {'name': name, 'rank': rank}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    return df
#################################################################################
def main():
    warnings.simplefilter('ignore')
    base_url = 'https://boardgamegeek.com/xmlapi2/'
    user = 'torisnow'

    #  get collection data
    collection_df = get_collection(user, base_url)
    plays_df = get_plays(user, base_url)
    hot_list_df = get_hot_list(base_url)

    # clean
    collection_df = clean_data(collection_df)

    # what is the oldest game in tori's collection?
    oldest = collection_df[collection_df['year'] == collection_df['year'].min()]
    print('Oldest Game in Collection: ' + oldest['name'].iloc[0] + ' - ' + oldest['year'].iloc[0])
    collection_by_year = collection_df['year'].value_counts().sort_index()
    games_by_year_df = pd.DataFrame({'Year': collection_by_year.index, 'Count': collection_by_year.values})

    # bar graph by plotly
    # plot = px.bar(games_by_year_df, x='Year', y='Count', title='Games by Year')
    # plot.show()

    # how many games are in each category/mechanic?
    # Categories have the prefix 'Category: ' and mechanics have the prefix 'Mechanic: ')
    categories_df = collection_df.iloc[:, 1:].filter(like='Category: ').sum().reset_index()
    categories_df.columns = ['Category', 'Count']
    top_10_categories = categories_df.nlargest(10, 'Count').sort_values('Count', ascending=True)

    plt.barh(top_10_categories['Category'], top_10_categories['Count'], color='skyblue')
    plt.xlabel('Number of Games')
    plt.ylabel('Categories')
    plt.title('Top 10 Categories by Number of Games')
    plt.tight_layout()
    plt.show()

    mechanics_df = collection_df.iloc[:, 1:].filter(like='Mechanic: ').sum().reset_index()
    mechanics_df.columns = ['Mechanic', 'Count']
    top_10_mechanics = mechanics_df.nlargest(10, 'Count').sort_values('Count', ascending=True)

    plt.barh(top_10_mechanics['Mechanic'], top_10_mechanics['Count'], color='skyblue')
    plt.xlabel('Number of Games')
    plt.ylabel('Mechanic')
    plt.title('Top 10 Mechanics by Number of Games')
    plt.tight_layout()
    plt.show()

    # what is the most popular publisher for tori's games?
    

    # based on the categories, mechanics, and publishers Tori already has, what are some recommendations for new games?
    # use the hot list to find games that are currently popular
    # or use rankings to find games that are highly rated



#################################################################################
if __name__ == '__main__':
    main()