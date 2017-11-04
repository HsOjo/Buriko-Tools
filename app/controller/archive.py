from ..model.buriko_archive import BurikoArchive


class Archive:
    @staticmethod
    def action(action):
        return {
            'create': Archive.create_by_dirs,
            'extract': Archive.extract,
        }.get(action, Archive.help)

    @staticmethod
    def help(param):
        print('''Actions:
        create(path_out, file1, file2, ...)
        extract(path_in, path_out)
        ''')

    @staticmethod
    def create_by_dirs(param):
        BurikoArchive.create_by_dir(param[0], *param[1:])

    @staticmethod
    def extract(param):
        io = BurikoArchive(param[0])
        io.extract_all(param[1])
        io.close()

