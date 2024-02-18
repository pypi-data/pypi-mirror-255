import os

from pypers.utils import utils as ut
from pypers.core.interfaces.db import get_operation_db, get_db_error, get_db_config
from pypers.core.interfaces import msgbus
import glob
import json
from pypers.steps.base.step_generic import EmptyStep
from pypers.utils.utils import clean_folder, delete_files


class Notify(EmptyStep):

    spec = {
        "version": "2.0",
        "descr": [
            "Notifies by email about the update"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "flag",
                    "descr": "flag that index is done",
                },
            ],
            "params": [
                {
                    "name": "reply_to",
                    "descr": "email sender",
                    "value": "gbd@wipo.int"
                }
            ]
        }
    }

    def process(self):
        self.collection_name = self.collection.replace('_harmonize', '')
        if self.is_operation:
            if 'em' in self.collection_name:
                get_operation_db().completed(self.run_id, 'emap')
            else:
                get_operation_db().completed(self.run_id, self.collection_name)
        stage_ori_root = os.path.join(os.environ.get('ORIFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        default_recpients = ['stefan-gabriel.chitic@wipo.int', 'nicolas.hoibian@wipo.int']
        manifests_path = os.path.join(stage_ori_root, '*', '*', 'manifest.json')
        manifests_files = list(glob.glob(manifests_path))

        # Errors
        errors = get_db_error().get_error(self.run_id, self.collection)
        if len(errors):
            error_report = {
                x['original_message']['step']+x['original_message']['index']:x['error_trace'] for x in errors}
            subject = "Errors in images or document processing %s in %s" % (self.collection, self.run_id)
            html = ut.template_render(
                'notify_errors.html',
                collection=self.collection,
                reports=error_report,
                runid=self.run_id)
            ut.send_mail(
                self.reply_to, default_recpients, subject, html=html, server=os.environ.get("MAIL_SERVER", None),
                password=os.environ.get("MAIL_PASS", None), username=os.environ.get("MAIL_USERNAME", None))
        else:
            recipients = list(set(default_recpients + get_db_config().get_email(self.collection_name)))
            # Report
            report = {}
            total_makrs = 0
            total_imgs = 0
            for manifest in manifests_files:
                with open(manifest, 'r') as f:
                    m_data = json.load(f)
                for appnum in m_data.get('files', {}).keys():
                    item = m_data['files'][appnum]
                    archive_name = os.path.basename(item.get('archive_file'))
                    if not report.get(archive_name, None):
                        report[archive_name] = {
                            'marks': 0,
                            'images': 0
                        }
                    if item.get('data', {}).get('ori', {}) and not os.path.exists(item['data']['ori']):
                        report[archive_name]['marks'] += 1
                        total_makrs += 1
                    for img in item.get('imgs', []):
                        if img.get('ori', {}) and not os.path.exists(img['ori']):
                            report[archive_name]['images'] += 1
                            total_imgs += 1

            full_report = {
                'marks': total_makrs,
                'images': total_imgs,
                'archive': report,
                'archives': report.keys(),
            }
            if full_report and full_report['marks'] != 0:
                collection =  self.collection_name
                collection_type = self.pipeline_type

                subject = "%s %s data update in WIPO's Global %s Database" % (
                    collection.upper()[0:2], collection.upper()[2:4],
                    self.pipeline_type)
                html = ut.template_render(
                    'notify_%s_update.html' % collection_type,
                    report=full_report)
                ut.send_mail(
                    self.reply_to, recipients, subject, html=html, server=os.environ.get("MAIL_SERVER", None),
                    password=os.environ.get("MAIL_PASS", None),
                    username=os.environ.get("MAIL_USERNAME", None))

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*json'])
        clean_folder(pipeline_dir)
