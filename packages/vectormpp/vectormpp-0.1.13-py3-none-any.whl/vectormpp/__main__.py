import os, sys, shutil, argparse, logging, traceback, multiprocessing
from datetime import datetime
from vectormpp.loggers import initCentralLogger, initWorkerLogger
from vectormpp.executor import Executor
from vectormpp.manifest import Manifest
from vectormpp import __version__

class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, ['all'])

def main():
    parser = argparse.ArgumentParser(description = 'Install/Uninstall VectorMPP Resource(s)', allow_abbrev = False)
    parser.add_argument("--manifest", dest = 'workdir', default = "", type = str, help = 'The Manifest Directory, if not specified, use The Current Working Directory.')
    parser.add_argument("--rundir", default = "", type = str, help = 'The Working Directory, if not specified, use "The Manifest Directory/runs/TIMESTAMP".')
    parser.add_argument("--loglevel", default = "info", choices = ['debug', 'info', 'warning', 'error'], help = 'Verbose Level')
    parser.add_argument('--set', action='append', type=lambda kv: kv.split("="), dest='settings', help='Overwrite Resrouces')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install", "--upgrade", "--install_or_upgrade", dest = "install_or_upgrade", nargs='*', action = CustomAction, help = 'Install/Upgrade Resource(s)')
    group.add_argument("--uninstall", nargs = '*', action = CustomAction, help = 'Uninstall Resource(s)')
    group.add_argument("--graph", help=argparse.SUPPRESS, action = "store_true")
    parser.add_argument("--version", action = "store_true", help = 'Print the Version')
    args = parser.parse_args()

    if len(sys.argv) == 1 or not (args.install_or_upgrade or args.uninstall or args.graph or args.version):
        parser.print_help()
        parser.exit()

    if args.version:
        print(__version__)
        return

    if not args.workdir:
        args.workdir = os.getcwd()

    if not args.rundir:
        args.rundir = os.path.join(args.workdir, 'runs', datetime.now().strftime("%Y%m%d%H%M%S"))
        os.makedirs(args.rundir, exist_ok=True)

    logger_queue = multiprocessing.Queue(-1)
    logger_process = multiprocessing.Process(target = initCentralLogger, args = (logger_queue, args.rundir, args.loglevel), name = "LogProcess")
    logger_process.start()

    try:
        code = 0
        initWorkerLogger(logger_queue, args.loglevel)
        logger = logging.getLogger(__name__)
        logger.info(f"{multiprocessing.current_process().name} starts.")
        logger.info(f"Working Directory: {args.workdir}.")

        if not shutil.which("helm"):
            logger.error("Cannot find 'helm' executable")
            return
        if not shutil.which("kubectl"):
            logger.error("Cannot find 'kubectl' executable")
            return

        manifest = Manifest(args.workdir, args.rundir, args.settings)
        if not manifest.initialise():
            return

        if args.graph:
            manifest.print_graph()
            return

        if args.uninstall:
            action = "uninstall"
            manifest.reverse_dependencies()
            manifest.set_targets(args.uninstall)
        else:
            action = "install_or_upgrade"
            manifest.set_targets(args.install_or_upgrade)

        executor = Executor(manifest.generate_shared_resources(), multiprocessing.Lock(), multiprocessing.Event(), logger_queue, args.loglevel)
        processes = [multiprocessing.Process(target = executor.start, args = (action,), name = f"ProcessNo.{i}") for i in range(3)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        if executor.event.is_set():
            code = 1
    except Exception as e:
        logger.error(f"Receive Exception:\n{traceback.format_exc().strip()}")
        code = 1
    finally:
        logger.info(f"{multiprocessing.current_process().name} ends.")
        logger_queue.put(None)
        logger_process.join()
        sys.exit(code)

if __name__ == '__main__':
    main()
