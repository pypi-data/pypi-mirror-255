import time

from zetsubou.utils import logger
from zetsubou.utils.busy_indicator import BusyIndicator
from zetsubou.utils.error_codes import EErrorCode, ReturnErrorcode

def execute_stage(func, succ_msg: str, err_code: EErrorCode):
    indicator_disabled = logger.IsVisible(logger.ELogLevel.Verbose) or logger.IsIde()

    start_time = time.time()

    with BusyIndicator(not indicator_disabled):
        result = func()

    end_time = time.time()

    if result is not None and result is not False:
        elapsed = end_time - start_time
        resolution = 2 if elapsed > 0.01 else 3
        logger.Success(f'{succ_msg} - {elapsed:.{resolution}f}sec')
        return result
    else:
        raise ReturnErrorcode(err_code)
