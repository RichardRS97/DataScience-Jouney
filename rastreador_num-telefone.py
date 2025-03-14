import requests

# Substitua pela sua chave de API da apilayer
access_key = "063b09ee5110f055c79e74d2e4e9e926"
# Sua chave OpenCage
open_cage_api_key = "cee21f3875ff4abc8cafced8510e8ec1"  

# Número a ser rastreado, sem formatação
phone_number = "+5519983483876"

# URL da API de validação de número de telefone com a chave de API e o número
url = f"http://apilayer.net/api/validate?access_key={access_key}&number={phone_number}"

# Fazendo a requisição à API de validação de número
response_geo = requests.get(url)

# Verificando a resposta da API
if response_geo.status_code == 200:
    try:
        geo_data = response_geo.json()  # Tentando obter dados no formato JSON

        # Verificando se o número é válido
        if geo_data['valid']:
            print(f"Numero: {geo_data['number']}")
            print(f"Formato Internacional: {geo_data['international_format']}")
            print(f"Código do País: {geo_data['country_code']}")  # Código do país
            print(f"Nome do País: {geo_data['country_name']}")  # Nome do país
            print(f"Operadora: {geo_data['carrier']}")
            print(f"Tipo de Linha: {geo_data['line_type']}")

            # Se o número for válido, obtenha cidade, latitude e longitude
            # Usando o código do país e a operadora para tentar determinar a localização
            country_name = geo_data['country_name']
            city_name = geo_data['location']  # Localização (se disponível)

            # Se houver dados de cidade e localização, faça uma nova requisição para obter as coordenadas
            if city_name:
                geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={open_cage_api_key}"
                geo_response = requests.get(geo_url)
                if geo_response.status_code == 200:
                    geo_info = geo_response.json()
                    if geo_info['results']:
                        # Extrair latitude, longitude e cidade
                        latitude = geo_info['results'][0]['geometry']['lat']
                        longitude = geo_info['results'][0]['geometry']['lng']
                        city = geo_info['results'][0]['components'].get('city', 'Cidade não encontrada')
                        print(f"Cidade: {city}")
                        print(f"Latitude: {latitude}")
                        print(f"Longitude: {longitude}")
                    else:
                        print("Não foi possível encontrar a cidade com as informações fornecidas.")
                else:
                    print("Erro ao obter dados de geolocalização.")
            else:
                print("Cidade não encontrada na resposta da API.")
        else:
            print(f"O número {geo_data['number']} não é válido.")
            print(f"País: {geo_data['country_name']}")
            print(f"Código do País: {geo_data['country_code']}")

    except requests.exceptions.JSONDecodeError:
        print("Erro: A resposta da API não é um JSON válido.")
else:
    print(f"Erro: API retornou status {response_geo.status_code}")
    print(f"Resposta da API: {response_geo.text}")
