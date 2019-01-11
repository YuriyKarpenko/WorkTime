

class Db:

    @staticmethod
    def load_file(filename: str) -> str or None:
        if filename:
            try:
                with open(filename, 'rt') as f:
                    data = f.read()
                return data
            except FileNotFoundError:
                pass
        return None

    @staticmethod
    def save_file(data: str, filename: str) -> bool:
        if filename and data:
            try:
                with open(filename, 'wt') as f:
                    f.write(data)
                return True
            except OSError:
                raise
        return False


db = Db()
