import logging


class Version:
    @staticmethod
    def get_version():
        return open('version.txt', 'r').read().strip()

    @staticmethod
    def get_app_name():
        try:
            return open('app_name.txt', 'r').read().strip()
        except Exception as e:
            logging.getLogger().error(e)
            return 'no_app_name'
