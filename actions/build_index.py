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
    def run(self, source, index_location, org_url):
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
                        "name": pack,
                        "pack_dir": pack_dir,
                        "pack_yaml_dir": pack_yaml_dir,
                        "pack_yaml_exists": pack_yaml_exists
                    }
                    continue


                pack_data = self._parse_yaml_file(pack_yaml_dir)

                if not pack_data:
                    index[pack] = {
                        "pack_data": pack_data,
                        "pack_yaml_dir": pack_yaml_dir
                    }
                elif "name" not in pack_data:
                    pack_data["repo_url"] = org_url + "/" + "undefined"
                    packs["undefined"] = pack_data
                else:
                    pack_data["repo_url"] = org_url + "/" + pack_data["name"]
                    packs[pack_data["name"]] = pack_data

                    


            # set metadata
            index["metadata"] = {
                "generated_ts": time.time(),
                "hash": self.hash_packs(index["packs"])
            }
            index["packs"]: packs

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