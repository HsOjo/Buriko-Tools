from os import walk

from ..model.buriko_archive import BurikoArchive
from ..model.buriko_script import BurikoScript
from ..model.buriko_image import BurikoImage


class Test:
    @staticmethod
    def action(action):
        return Test.main

    @staticmethod
    def main(param):
        # bs = BurikoScript()
        # bs.load('./other/__shortcut', True)
        # bs.save('./data_test/1_10_030', False)
        # for nd, ds, fs in walk('./data_new_json'):
        #     for f in fs:
        #         if f[0] != '.':
        #             # bs.load('%s/%s' % (nd, f), True)
        #             bs.load_json('%s/%s' % (nd, f))
        #             # bs.translate()
        #             bs.save('./data_new/%s' % f[:-5], False)
        #             # bs.save_json('./data_new_json/%s.json' % f)
        #             print(f, 'ok')
        #     break
        # BurikoArchive.create_by_dir('data01100.arc', './data_new', './other')
        ba = BurikoArchive('/Volumes/NTFS/Game/eroge/11月のアルカディア/data04100.arc')
        ba.extract_all('data_04100')
        # bi = BurikoImage('data_02100/00_00_00_不2')
        # bi = BurikoImage('data_02100/00_00_00_呆')
        # bi = BurikoImage('data_02100/00_00_00_驚')
        # bi = BurikoImage('data_02100/00_00_00_怒')
        # bi = BurikoImage('data_02100/00_00_00_通')
        # bi = BurikoImage('data_02100/00_00_00_通2')
