from ..model.buriko_script import BurikoScript


class Script:
    @staticmethod
    def action(action):
        return {
            'to_json': Script.to_json,
            'from_json': Script.from_json,
        }.get(action, Script.help)

    @staticmethod
    def help(param):
        print('''Actions:
        to_json(load_raw, path_in, path_out)
        from_json(path_in, save_raw, path_out)
        ''')

    @staticmethod
    def to_json(param):
        bs = BurikoScript()
        bs.load(param[1], param[0] == 'true')
        bs.save_json(param[2])

    @staticmethod
    def from_json(param):
        bs = BurikoScript()
        bs.load_json(param[0])
        bs.save(param[2], param[1] == 'true')
