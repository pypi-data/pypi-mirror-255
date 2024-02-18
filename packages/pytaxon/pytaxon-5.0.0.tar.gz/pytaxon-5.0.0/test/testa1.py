import requests
from pprint import pprint
import pandas as pd

df = pd.read_excel("F:/0 - Bibliotecas Windows/Downloads/Opiliones_spreadsheet.xlsx")

def verificar_taxon(nome_taxon, id):
    valid_ranks = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    url = "http://resolver.globalnames.org/name_resolvers.json"
    params = {
        'names': nome_taxon,
        'best_match_only': True,
        'with_vernaculars': True, 
        'with_context': True,
        'with_canonical_ranks': True, 
        'data_source_ids': id,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['data'][0]['is_known_name']:
            service = data['data'][0]['results'][0]
            paths = service['classification_path'].split('|')
            ids = service['classification_path_ids'].split('|')
            ranks = service['classification_path_ranks'].split('|')

            result = {}

            for i, rank in enumerate(ranks):
                if rank in valid_ranks:
                    result[rank] = [paths[i], ids[i] if ids != [''] else 'No ID']
            result['scientificName'] = [service['name_string'], service['taxon_id'] if service['taxon_id'] != [''] else 'No ID']
                
            for rank in valid_ranks:
                if rank not in result:
                    result[rank] = ['No Data', 'No ID']

            return result
        else:
            return 'Unknown name'

# for specie in df['verbatimScientificName']:
nome_taxon_usuario = 'Thelyphonidae'
resultado = verificar_taxon(nome_taxon_usuario, 11)
pprint(resultado)
