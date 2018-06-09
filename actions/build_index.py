import os
import json
import yaml
import time
import md5
import hashlib
from st2common.runners.base_action import Action

class BuildIndex(Action):
    '''
    Builds an index.json for an organization
    '''
    def run(self, source, index_location, resource_types):
        """
        `source` can be:
        A directory like: 
        '/opt/stackstorm/bitovi-stackstorm-exchange'

        or (todo)
        A github organization like:
        'https://github.com/bitovi-stackstorm-exchange'

        `index_location`
        The location to save the index file:
        `/opt/stackstorm/bitovi-stackstorm-exchange/index.json`
        """
        index = {
            "packs": {}
        }

        if os.path.isdir(source):
            parent_dir = os.path.dirname(os.getcwd())
            packs = {}
            for pack in os.listdir(source):
                pack_dir = source + "/" + pack
                pack_yaml_dir = pack_dir + '/pack.yaml'
                pack_yaml_exists = os.path.isfile(pack_yaml_dir)
                if not pack_yaml_exists:
                    packs[pack] = {
                        "pack_dir": pack_dir,
                        "pack_yaml_dir": pack_yaml_dir,
                        "pack_yaml_exists": pack_yaml_exists
                    }
                    continue

                pack_data = self._parse_yaml_file(pack_yaml_dir)


                packs[pack_data["name"]] = pack_data
                pack_data["repo_url"] = "https://github.com/bitovi-stackstorm-exchange/" + pack_data["name"]


            # set metadata
            index["metadata"] = {
                "generated_ts": time.time(),
                "hash": self.hash_packs(index["packs"]),
                "packs": packs
            }

        if index and index_location is not None:
            with open(index_location, 'w') as outfile:
                json.dump(index, outfile)

        return index

        


    def _parse_yaml_file(self, file_path):
        with open(file_path) as data_file:
            details = yaml.load(data_file)
        return details


    def hash_packs(self, obj):
        h = hashlib.new('ripemd160')
        h.update(json.dumps(obj))
        return h.hexdigest()

    def format_resource_components(self, resource_type, resource_dir, resource_components):
        components = []
        for component in resource_components:
            if not component.endswith('.yaml'):
                continue

            componentData = self._parse_yaml_file(component)
            components.append(componentData['name'])

        return comonents


    def get_resource(self, resource_type, pack_dir, pack_data):
        resource = {}
        resource_dir = pack_dir + "/" + resource_type
        if os.path.isdir(resource_dir):
            resource_components = os.listdir(resource_dir)
            resource = {
                "count": len(resource_components),
                "resources": self.format_resource_list(resource_type, resource_dir, resource_components)
            }
        else:
            return False

        return resource 


    def get_content(self, pack_dir, pack_data, resource_types):
        content = {}

        for resource_type in resource_types:
            resource = self.get_resource(resource_type, pack_dir, pack_data)
            if resource:
                content[resource_type] = resource
        
        return content