import ipih

def start() -> None:
    from MobileHelperService.service import MobileHelperService, checker
    MobileHelperService(checker=checker).start(True)

if __name__ == '__main__':
    start()
