import datetime
import logging
import os
import sys


class LoggerSupplier:
    """
        Configure log_logger_supplier

        :param path_to_log_directory:  path to directory to write log file in
        :return:
        """

    def __init__(self, name_prefix, path_to_log_directory, log_level):
        print("Log_logger_supplier starting ...")
        log_filename = name_prefix + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s : %(filename)s[LINE:%(lineno)d]: %(levelname)s : %(message)s')
        u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
        init_logger_error_message = None
        try:
            fh = logging.FileHandler(filename=os.path.join(path_to_log_directory, log_filename))
            fh.setLevel(log_level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        except Exception as e:
            print(F"Error in logger init={e}")
            print(F"Try to set current directory...")
            try:
                fh = logging.FileHandler(filename=os.path.join("", log_filename))
                fh.setLevel(log_level)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
                print(F"Log directory have set to current directory successfully")
                init_logger_error_message = F"Log directory have set to current directory. Error in logger init={e} "
            except Exception as e:
                print(F"Error in set log directory {e}")
                print(F"Logs are printed only in terminal")

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(log_level)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        if init_logger_error_message:
            self.logger.error(init_logger_error_message)

    def get_logger(self):
        return self.logger
