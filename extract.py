import requests

def get_metadata():
    url = "https://data.humdata.org/api/action/package_show"
    params = {
        "id": "explosive-weapons-use-affecting-aid-access-education-and-healthcare-services"
    } 
    response = requests.get(url, params=params) 
    response.raise_for_status() 
    data = response.json()
    return data


def find_resource_url(metadata):
    result = metadata['result'] 
    resources = result['resources']
    
    for resource in resources:
        if "Incident Data" in resource['name'] and resource['name'].startswith('2020-'):
            return resource['url']
        
    raise ValueError("Resource not found")
    

def download_file(downloaded_url, filename):
    file_response = requests.get(downloaded_url)
    file_response.raise_for_status()
    with open(
        filename,
        "wb"
        ) as file:
        file.write(file_response.content)
        print('File saved')

def main():
    metadata = get_metadata()
    downloaded_url = find_resource_url(metadata)
    download_file(downloaded_url, "explosive_weapon_raw.xlsx")

if __name__ == '__main__':
    main()