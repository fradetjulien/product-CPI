import json
import click
import requests
from matplotlib import pyplot as plt

def build_graph(data):
    '''
    Build the final graph
    '''
    plt.plot(data["periods"], data["values"])
    plt.legend(data["series_id"])
    plt.ylabel('CPI')
    plt.xlabel('Period')
    plt.xticks(rotation=90)
    plt.title('Product CPI over time')
    plt.show()

def init_dictionnary():
    '''
    Initialize a new dictionnary and set empty lists inside
    '''
    new_dictionnary = {
        "series_id": [],
        "periods": [],
        "values": []
    }
    return new_dictionnary

def store_data(data):
    '''
    Store and sort the data retrieved from the API request
    '''
    sort_data = init_dictionnary()
    try:
        for series in data:
            sort_data["series_id"].append(series['seriesID'])
            for item in series['data']:
                sort_data["periods"].append(item['year'] + ' ' + item['periodName'])
                sort_data["values"].append(float(item['value']))
        sort_data["periods"].reverse()
        sort_data["values"].reverse()
    except:
        print("Sorry, failure during computing API request result.")
        return None
    return sort_data

def check_status(data, product_id, status):
    '''
    Check if the GET request has successfully recover data
    '''
    if 'Series does not exist for Series ' + str(product_id) in data['message'] \
        or status == 404 or status == 400:
        print("Sorry, the product ID was incorrect.")
        return False
    elif status == 401:
        print("Sorry, you're not authorized to make this request.")
        return False
    elif data['status'] == 'REQUEST_NOT_PROCESSED' or status == 429:
        print("Sorry, you request could not have been treated. " \
              "Unregistered users may request up to 25 queries daily.")
        return False
    else:
        return True

def request_data(product_id, start_year, end_year):
    '''
    Retrieve data from the public API
    '''
    ranges = {'startyear': start_year, 'endyear': end_year}
    try:
        request = requests.get('http://api.bls.gov/publicAPI/v2/timeseries/data/' + product_id
                               + '.json', params=ranges)
        data = json.loads(request.text)
        if not check_status(data, product_id, request.status_code):
            return None
    except ValueError:
        print("Error while loading JSON.")
        return None
    return data

def is_range_correct(start_year, end_year):
    '''
    Check if start year and the end year are consistent
    '''
    if start_year > end_year:
        print("You can't specify an end year that previous the start year.")
        return False
    if start_year < 1995:
        print("Sorry, we can't retrieve data previous 1995.")
        return False
    return True

@click.group()
def cli():
    '''
    Find all the CPI between a start year and an end year for a specific product
    '''

@cli.command('product')
@click.argument('product_id')
@click.option('--startyear', '-s', default=2009, type=int)
@click.option('--endyear', '-e', default=2019, type=int)
def build_cpi(product_id, startyear, endyear):
    '''
    Manage all steps in order to build the final graph
    '''
    if is_range_correct(startyear, endyear):
        data = request_data(product_id, startyear, endyear)
    if data:
        data = store_data(data['Results']['series'])
    if data:
        build_graph(data)

if __name__ == '__main__':
    cli()
