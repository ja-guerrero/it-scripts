def init_logging():
    from datetime import datetime
    import logging
    from logging import handlers

    dt_now = datetime.today().strftime('%Y%m%d')

    # Set up logging 
    log_file = ("./logs/logs.txt")
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    file_handle = logging.FileHandler(log_file)
    stream_handle = logging.StreamHandler()
    file_handle.setLevel(logging.DEBUG)
    stream_handle.setLevel(logging.DEBUG)
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handles = [file_handle, stream_handle]
    for handle in handles:
        handle.setFormatter(log_format)
        logger.addHandler(handle)