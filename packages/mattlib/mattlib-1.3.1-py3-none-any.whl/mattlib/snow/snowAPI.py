import sys
sys.path.append('../mattlib')
from mattlib.BaseAPI import BaseAPI
import pandas as pd
import requests as rq
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import os

# Authorization must contain fields:
#    url
#    username
#    password

class snowAPI(BaseAPI):
    required_info = [
        ("url", "str"),
        ("username", "str"),
        ("password", "str")
    ]

    def connect(self, url, username, password):
        self.url = url.rstrip()
        self.username = username.rstrip()
        self.password = password.rstrip()
        rq.get(self.url, headers={"Accept": "application/json"}, auth=(self.username, self.password)).json()

    def get_user_status(self, user_id):
        # Obtém o status de um usuário com base no ID
        urlf = f"{self.url}users/{user_id}/"
        response = rq.get(urlf, headers={"Accept": "application/json"}, auth=(self.username, self.password)).json()
        body = pd.json_normalize(response['Body'])
        return body

    def get_users_status_parallel(self, data):
        # Executa a obtenção de status de usuários em paralelo
        df = pd.DataFrame()
        with ThreadPoolExecutor() as executor:
            futures = []
            for user_id in data['Body.Id']:
                futures.append(executor.submit(self.get_user_status, user_id))
            for future in futures:
                try:
                    body = future.result()
                    df = pd.concat([df, body])
                except Exception as e:
                    print(f"Erro durante a execução: {e}")
        return df

    def process_batch(self, ids, data):
        df = pd.DataFrame()
        for user_id in ids:
            urlf = f"{self.url}users/{user_id}/applications/"
            try:
                response = rq.get(urlf, headers={"Accept": "application/json"}, auth=(self.username, self.password), timeout=None).json()
                if len(response['Body']) != 0:
                    body = pd.json_normalize(response['Body'])
                    id_sam = data.loc[data['Body.Id'] == user_id, 'Body.Username'].values[0].split('\\')[1]
                    nome = data.loc[data['Body.Id'] == user_id, 'Body.FullName'].values[0]
                    body['onPremisesSamAccountName'] = id_sam
                    body['Nome completo'] = nome
                    body = body[body['Body.ManufacturerName'] == 'Microsoft Corporation']
                    df = pd.concat([df, body])
            except requests.exceptions.ConnectTimeout as e:
                print(f"Erro de tempo limite: {e}")
        return df

    def get_user_applications_parallel(self, data):
        df = pd.DataFrame()
        batch_size = 1000  # Ajuste o tamanho do lote conforme necessário
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(0, len(data), batch_size):
                batch_ids = data['Body.Id'].iloc[i:i+batch_size].tolist()
                futures.append(executor.submit(self.process_batch, batch_ids, data))
            
            for future in concurrent.futures.as_completed(futures):
                df = pd.concat([df, future.result()])
        
        return df

    def get_userInfo(self):
        batch_size = 1000
        num = 0
        # Obtém informações de usuários em lotes
        data = pd.DataFrame()
        while True:
            urlf = f"{self.url}users/?%24top={batch_size}&%24skip={num}"
            response = rq.get(urlf, headers={"Accept": "application/json"}, auth=(self.username, self.password)).json()
            if len(response['Body']) == 0:
                break
            body = pd.json_normalize(response['Body'])
            data = pd.concat([data, body])
            num += batch_size
        return data

    def userApplication(self):
        data = self.get_userInfo()
        df_application = self.get_user_applications_parallel(data)
        return df_application

    def users(self):
        data = self.get_userInfo()
        # Obtém o status dos usuários em paralelo
        data_users = self.get_users_status_parallel(data)
        data_users = data_users[['Username', 'StatusCode', 'FullName']]
        data_users['Username'] = data_users['Username'].str.split('\\').str[1]
        data_users.rename(columns={'Username': 'onPremisesSamAccountName',
                            'StatusCode':'Status',
                            'FullName':'Nome completo'}, inplace=True)
        return data_users
    
    def methods(self):
        # Retorna informações sobre os métodos disponíveis na API
        methods = [
            {
                'method_name': 'users',
                'method': self.users,
                'format': 'json'
            },
            {
                'method_name': 'userApplication',
                'method': self.userApplication,
                'format': 'json'
            },
        ]
        return methods