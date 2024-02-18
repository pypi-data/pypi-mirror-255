from typing import List, Optional

from cirro.api.clients.utils import filter_deleted
from cirro.api.models.file import FileAccessContext
from cirro.api.models.project import Project
from cirro.api.models.reference import Reference, References
from cirro.api.services.base import fetch_all_items
from cirro.api.services.file import FileEnabledService
from cirro.file_utils import filter_files_by_pattern


class ProjectService(FileEnabledService):
    def list(self) -> List[Project]:
        """
        Gets a list of projects that you have access to
        """
        query = '''
          query ListProjects(
            $filter: ModelProjectFilterInput
            $limit: Int
            $nextToken: String
          ) {
            listProjects(filter: $filter, limit: $limit, nextToken: $nextToken) {
              items {
                id
                name
                desc
                status
              }
              nextToken
            }
          }
        '''

        items = fetch_all_items(self._api_client, query, {})
        not_deleted = filter_deleted(items)
        return [Project.from_record(item) for item in not_deleted]

    def find_by_name(self, name: str) -> Optional[Project]:
        """
        Finds a project by name
        """
        return next((p for p in self.list() if p.name == name), None)

    def get_reference_types(self, project_id: str) -> List[str]:
        """
        Gets the list of reference types which are available in a project
        """
        ref_prefix = "data/references/"
        access_context = FileAccessContext.download_project_resources(project_id)
        resources = self._file_service.get_file_listing(access_context)
        reference_files = filter_files_by_pattern(resources, f'{ref_prefix}*/*/*')
        return list(set([file.relative_path[len(ref_prefix):].split("/", 1)[0] for file in reference_files]))

    def get_references(self, project_id: str, reference_directory: str) -> References:
        """
        Gets a list of references available for a given project and reference directory
        """
        access_context = FileAccessContext.download_project_resources(project_id)
        resources = self._file_service.get_file_listing(access_context)
        reference_files = filter_files_by_pattern(resources, f'data/references/{reference_directory}/*/*')
        references = [*set(Reference.of(file) for file in reference_files)]
        references = sorted(references, key=lambda r: r.name.lower())
        return References(references)
