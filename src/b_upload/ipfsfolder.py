import os

import ipfsapi

from .utils import cleanup_after, changewd


@cleanup_after
def add_ipfs_file(file_path):
    """ Add a file to IPFS. Optionally clean up.

    Returns:
        dict: Response with IPFS files.
    """
    ipf = IpfsFile()
    ipfs_hash = ipf.add(file_path)

    return ipfs_hash


@cleanup_after
def add_ipfs_folder(folder_path):
    """ Recursively add a directory to IPFS.

    Returns:
        dict: Response with root hash and IPFS files.
    """
    ipf = IpfsFolder()
    hashes = ipf.add(folder_path)
    if len(hashes) > 0:
        ipfs_root = ipf.find_hash(hashes, name="")
        return dict(
            root=ipfs_root,
            files=hashes,
        )
    return dict()


class IpfsManager:
    def __init__(self):
        self.api = ipfsapi.Client(host=os.getenv("IPFS_API_HOST", "localhost"))

    def folder_links(self, root_hash):
        return self.api.object_links(root_hash)['Links']

    def add_size_info(self, hash_list):
        return list(map(self.add_size, hash_list))

    def strip_root_folder(self, hash_list):
        return list(map(self.strip_root, hash_list))

    def add_size(self, hash_obj):
        hash_obj['Size'] = self.api.object_stat(hash_obj['Hash'])['CumulativeSize']
        return hash_obj

    def add_folder(self, path):
        res = self.api.add(path, recursive=True)
        if type(res) is dict:
            return [res]
        return res

    @staticmethod
    def strip_root(hash_obj):
        if "Name" in hash_obj:
            hash_obj['Name'] = "/".join(hash_obj['Name'].split('/')[1:])
        return hash_obj

    @staticmethod
    def find_hash(hash_list, name=""):
        root_obj = [x['Hash'] for x in hash_list if x['Name'] == name]
        return root_obj[0] if len(root_obj) == 1 else None


class IpfsFile(IpfsManager):
    def __init__(self):
        super().__init__()

    def add(self, path):
        res = self.api.add(path, recursive=False)
        return res


class IpfsFolder(IpfsManager):
    def __init__(self):
        super().__init__()

    def add(self, path):
        with changewd(path):
            res = self.add_folder(path.rstrip('/').split('/')[-1])
            return self.strip_root_folder(self.add_size_info(res))
