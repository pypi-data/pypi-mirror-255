# -*- coding: utf-8 -*-
# @Time    : 24/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm


import logging
import os
import pandas as pd
from colorama import init, Fore, Back, Style

script_path = os.path.dirname(os.path.abspath(__file__))
logger_aux = logging.getLogger(__name__)
Logg_option = True


def update_logg_file(msg: str, Typ: int = 0, logger=logger_aux, Logg: bool = Logg_option, Print: bool = True):
    """
    Creates or updates the log_py file. In addition, it prints the message formatted according to the type.

    :param msg: Message text to be displayed by console or saved in the log_py file
    :param logger: From function logging.getLogger(__name__)
    :param Typ: May be: 0(pass), 1(debug), 2(info) 3(warning), 4(error), and 5 (critical). Default=0
    :param Logg: boolean to enable or disable log_py file. Default=True
    :param Print: Display the message by console. Default=True
    :return: openpy_mdist.log
    """
    if Logg == True:

        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(msg)s'
        # To override the default severity of logging
        logger.setLevel('DEBUG')
        # logger = logging.getLogger(__name__)

        # Use FileHandler() to log_py to a file
        file_handler = logging.FileHandler(f"{script_path}\openpy_mdist.log")
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        # Don't forget to add the file handler
        logger.addHandler(file_handler)
        if Typ == 1:
            logger.debug(msg)
        if Typ == 2:
            logger.info(msg)
        if Typ == 3:
            logger.warning(msg)
        if Typ == 4:
            logger.error(msg)
        if Typ == 5:
            logger.critical(msg)

    if Print == True:
        if Typ == 0:
            print(Style.DIM + msg)
        else:
            # print('_' * 64)
            if Typ == 1:
                'debug'
                print(Style.NORMAL + msg + Style.RESET_ALL)
            if Typ == 2:
                'info'
                print(Style.BRIGHT + msg + Style.RESET_ALL)
            if Typ == 3:
                'warning'
                print(Fore.YELLOW + msg + Style.RESET_ALL)
            if Typ == 4:
                'error'
                print(Fore.RED + msg + Style.RESET_ALL)
            if Typ == 5:
                'critical'
                print(Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL)
