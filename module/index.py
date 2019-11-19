import click
import requests
import json

def check_status(data, product_id):
    '''
    Check if the GET request has successfully recover data
    '''
    if 'Series does not exist for Series ' + str(product_id) in data['message']:
        print("Sorry, the product ID was incorrect.")
        return False
    elif data['status'] == 'REQUEST_NOT_PROCESSED':
        print("Sorry, you request could not have been treated.")
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
        if not check_status(data, product_id):
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
def build_CPI(product_id, startyear, endyear):
    '''
    Manage all steps in order to build the final graph
    '''
    if is_range_correct(startyear, endyear):
        data = request_data(product_id, startyear, endyear)
        return data

if __name__ == '__main__':
    cli()
