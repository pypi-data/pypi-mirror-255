import biolib.api
from biolib.biolib_api_client.lfs_types import LargeFileSystemVersion, LargeFileSystem


class BiolibLargeFileSystemApi:

    @staticmethod
    def create(account_uuid: str, name: str) -> LargeFileSystem:
        response = biolib.api.client.post(
            path='/lfs/',
            data={'account_uuid': account_uuid, 'name': name},
        )

        lfs: LargeFileSystem = response.json()
        return lfs

    @staticmethod
    def fetch_version(lfs_version_uuid: str) -> LargeFileSystemVersion:
        response = biolib.api.client.get(
            path=f'/lfs/versions/{lfs_version_uuid}/',
        )

        lfs_version: LargeFileSystemVersion = response.json()
        return lfs_version

    @staticmethod
    def create_version(resource_uuid: str) -> LargeFileSystemVersion:
        response = biolib.api.client.post(
            path='/lfs/versions/',
            data={'resource_uuid': resource_uuid},
        )

        lfs_version: LargeFileSystemVersion = response.json()
        return lfs_version
