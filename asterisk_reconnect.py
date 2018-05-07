from asterisk_reconnect import configuration, reconnect, log, signal_handler
import time
import signal


def main():

    config = configuration.build_config("asterisk_reconnect.cfg")

    logger = log.config_logging(config['logger'])
    logger.info('asterisk_reconnect initializing')

    as_reconnect = reconnect.asterisk_reconnect(logger, config)
    sig_handler = signal_handler.signal_handler(logger, as_reconnect)

    # Setup signal handlers
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, sig_handler.handle_signal)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
