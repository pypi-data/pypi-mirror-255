class HOSTS:
    
    class SERVICES:

        NAME: str = "svshost"
        ALIAS: str = "zabbix"
        IP: str = "192.168.100.95"

    class BACKUP_WORKER:

        NAME: str = "backup_worker"
        ALIAS: str = "backup_worker"
        IP: str = "192.168.100.11"

    class WS255:

        NAME: str = "ws-255"
        IP: str = "192.168.100.138"

    class WS816:

        NAME: str = "ws-816"
        IP: str = "192.168.254.81"

    class WS735:

        NAME: str = "ws-735"
        ALIAS: str = "shared_disk_owner"
        IP: str = "192.168.254.102"

    class DEVELOPER(WS735):

        pass

    class DC1:

        NAME: str = "fmvdc1.fmv.lan"
        ALIAS: str = "dc1"
        IP: str = "192.168.100.4"

    class DC2:

        NAME: str = "fmvdc2.fmv.lan"
        ALIAS: str = "dc2"
        IP: str = "192.168.100.23"

    class PRINTER_SERVER(DC1):

        pass

    class POLIBASE:

        # shit - cause polibase is not accessable
        NAME: str = "fmvpolibase1.fmv.lan"
        ALIAS: str = "polibase"
        IP: str = "192.168.100.3"

    class POLIBASE_TEST:

        NAME: str = "fmvpolibase2.fmv.lan"
        ALIAS: str = "polibase_test"
        IP: str = "192.168.110.140"

    class _1C:

        NAME: str = "fmv1c2"
        ALIAS: str = "1c"
        IP: str = "192.168.100.22"

    class NAS:

        NAME: str = "nas"
        ALIAS: str = "nas"
        IP: str = "192.168.100.200"

    class PACS_ARCHVE:

        NAME: str = "pacs_archive"
        ALIAS: str = "ea_archive"
        IP: str = "192.168.110.108"