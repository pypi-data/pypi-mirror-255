#GCP
#Secret Manager
from google.cloud import secretmanager
#Resource Manager (para obtener project number)
from google.cloud import resourcemanager_v3

class adam_credmanager():
    def __init__(self, project_id, project_number=None) -> None:
        self.project_id=project_id
        self.project_number=project_number
        self.client= secretmanager.SecretManagerServiceClient()

    def list_secret_versions(self, secret_id: str) -> None:
        """
        List all secret versions in the given secret and their metadata.
        """

        # Build the resource name of the parent secret.
        parent = self.client.secret_path(self.project_id, secret_id)

        # List all secret versions.
        for version in self.client.list_secret_versions(request={"parent": parent}):
            last_ver=version.name
        return last_ver

    def get_secret(self, secret_id, version_id=None):
        """Devuelve objeto en secret manager"""
        
        if self.project_number == None: #Si no tiene definido el project id lo busca
            self.project_number=self.get_project_number(self.project_id)
            
        if version_id is not None:
            name=f"projects/{self.project_number}/secrets/{secret_id}/versions/{version_id}"
        else:
            name=self.list_secret_versions(secret_id)

        response = self.client.access_secret_version(request={"name": name})

        return response.payload.data.decode("UTF-8")



    @staticmethod #TODO: Funcion de soporte... No deberia estar aca... pero no se si la vamos a usar en otro lado
    def get_project_number(project_id) -> str:
        """Given a project id, return the project number"""
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.SearchProjectsRequest(query=f"id:{project_id}")
        page_result = client.search_projects(request=request)

        for response in page_result:
            if response.project_id == project_id:
                project = response.name
                return project.replace('projects/', '')
