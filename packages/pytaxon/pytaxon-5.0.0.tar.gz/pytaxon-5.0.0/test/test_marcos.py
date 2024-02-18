import requests
from pprint import pprint

nomes = ['GBIF Backbone Taxonomy', 'Catalogue of Life Checklist', 'iNaturalist Taxonomy', 'National Center for Biotechnology Information'] 

# def return_data(id):


def verificar_taxon(nome_taxon):
    valid_ranks = ['kingdom', 'phylum', 'class', 'order', 'family', 'species']
    url = "http://resolver.globalnames.org/name_resolvers.json"
    params = {
        'names': nome_taxon,
        'with_context': 'true'  # Para obter o caminho de classificação
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        service = data['data'][0]['results']
        if 'data' in data and data['data']:
            return [service[i] for i in range(len(service)) if service[i]['data_source_title'] in nomes]
            
        else:
            return "Resposta da API não contém os dados esperados"
    else:
        return f"Erro ao acessar a API: Status {response.status_code}"

nome_taxon_usuario = 'Bia actorion'
resultado = verificar_taxon(nome_taxon_usuario)
pprint(resultado)