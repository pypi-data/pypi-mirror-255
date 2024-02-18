def start() -> None:
    from MobileHelperService.service import MobileHelperService, checker
    from MobileHelperService.const import DEFAULT_COUNT
    MobileHelperService(DEFAULT_COUNT, checker).start()

if __name__ == '__main__':
    start()
