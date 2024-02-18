import os
import json
from pypers.core.interfaces import db
from gbdtransformation.parser import Parser
from pypers.utils.utils import appnum_to_subdirs
from . import BaseHandler

parsers = {}


class IdxTransform(BaseHandler):

    def process(self, data_file, appnum):
        if not len(data_file.get('doc', None)):
            return
        # transform to idx file
        if not parsers.get('solrjtm', None):
            parsers['solrjtm'] = Parser('solrjtm', type=self.pipeline_type)
        parser = parsers.get('solrjtm')
        record = data_file.get('doc', {})
        db.get_pre_prod_db().put_items([record['data_files']['latest']], as_obj=True)
        st13 = data_file.get('st13', None)

        self.data_files = []
        # no gbd file is set => nothing to transform
        if not record['data_files'].get('gbd'):
            return

        # attempt the transformation to an idx file
        try:
            idx_data = json.loads(parser.run(json.dumps(record['data_files']['gbd']),
                                             raise_errors=True))
            # amend the index data with collection
            idx_data['collection'] = self.collection
            # amend the index data with runid
            idx_data['runid'] = self.run_id
            # amend the index data with imgs crc
            for img_info in record.get('img_files', []):
                idx_data.setdefault('logo', [])
                idx_data['logo'].append(img_info['crc'])

            lire_data = record['data_files']['latest'].get('image_analysis', [])
            # To remove when solr is ready for multi_image
            if len(lire_data) > 0:
                idx_data.update(self.parse_lire_solr(lire_data))
            os.makedirs(os.path.join(self.extraction_dir, appnum_to_subdirs(appnum), st13), exist_ok=True)
            idx_file = os.path.join(self.extraction_dir, appnum_to_subdirs(appnum), st13, 'idx.json')
            with open(idx_file, 'w') as f:
                json.dump(idx_data, f, indent=2)
            record['idx'] = idx_file
        except Exception as e:
            self.logger.error("Error in transforming %s to solr: %s" % (st13, e))

    def convert_keys_type(self, input_dict):
        for key in input_dict.keys():
            if isinstance(input_dict[key], list):
                input_dict[key] = set(input_dict[key])
        return input_dict

    def parse_lire_solr(self, lires):
        to_return = self.convert_keys_type(lires[0])
        for lire in lires[1:]:
            for key in lire.keys():
                if isinstance(lire[key], list):
                    to_return[key] = to_return[key].union(set(lire[key]))
                else:
                    to_return[key] = '%s,%s' % (to_return[key], lire[key])
        for key in to_return.keys():
            if isinstance(to_return[key], set):
                to_return[key] = list(to_return[key])
        return to_return
