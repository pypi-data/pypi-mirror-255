import ipih

def start() -> None:
    from BackupService.service import start
    start(True)

if __name__ == "__main__":
    start()