import requests
import jwt


class KudafProcess:
    """
    A class to manage OAuth2 login to Feide for the Kudaf project
    """
    def __init__(self):
        self.state = None
        self.granted_variables = None
        self.basic_auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        self.config = self.get_config()

    def get_config(self) -> dict:
        _config = {}
        # Kudaf endpoints
        _config['permissions_endpoint'] = "https://kudaf-core.paas2.uninett.no/api/v1/permissions/"

        return _config

    async def get_permissions(self, jwt_token: str) -> dict:
        headers={
            "Authorization": "Bearer " + jwt_token,
            "Accept": "application/json",
        }
        response = requests.get(
                url=self.config.get('permissions_endpoint'),
                headers=headers,
        )
        print("Response Status: {}".format(response.status_code))
        print("Response Data: {}".format(response.json()))
        print("====================================================")
        print()

        if response.status_code != 200:
            project_blocks = []
        else:
            project_blocks = [p.get('authorizations') for p in response.json() \
                        if p.get('authorizations') is not None or p.get('authorizations') != "JWT"]

        granted_variables = {}
        for permissions_token in project_blocks:
            payload = jwt.decode(permissions_token, options={"verify_signature": False})
            project_name = payload.get('project_name')
            granted_variables[project_name] = {}
            for datasource_id, variables in payload['datasources'].items():
                for var in variables:
                    if not var['data_retrieval_url'] or var['data_retrieval_url'] is None:
                        continue
                    datasource_name = var.get('datasource_name', datasource_id)
                    if datasource_name not in granted_variables[project_name]:
                        granted_variables[project_name][datasource_name] = []

                    granted_variables[project_name][datasource_name].append(var)

        print("Granted_variables in KUDAF: {}".format(granted_variables))
        self.granted_variables = granted_variables

        return granted_variables

 
kudaf_process = KudafProcess()
