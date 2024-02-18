# Logger that can attach to widget and print log to widget

import logging
from logging import StreamHandler
from .debug import debug

"""
logger = Logger.get_logger()
logger_downloader = Logger.get_logger(Logger.DATA_DOWNLOADER)

Logger.detach_all_widgets_from_logger(Logger.DATA_DOWNLOADER)
Logger.attach_widget_to_logger(dialog.txt_log, Logger.DATA_DOWNLOADER)

logger_downloader.info('\n')


"""


class WidgetLogger:
    GENERAL = 'general'
    pool = {}

    @staticmethod
    def get_logger(name: str = GENERAL):
        if name in WidgetLogger.pool:
            return WidgetLogger.pool[name]['logger']

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(WidgetLogger.DebugLogHandler())
        WidgetLogger.pool[name] = {'logger': logger, 'attached_widgets': []}

        return logger

    @staticmethod
    def attach_widget_to_logger(widget, name: str = GENERAL):
        if name not in WidgetLogger.pool:
            WidgetLogger.get_logger(name)

        WidgetLogger.pool[name]['attached_widgets'].append(widget)
        WidgetLogger.pool[name]['logger'].addHandler(WidgetLogger.WidgetLogHandler(widget))

    @staticmethod
    def detach_widget_from_logger(widget, name: str = GENERAL):
        if name not in WidgetLogger.pool:
            return

        WidgetLogger.pool[name]['attached_widgets'].remove(widget)
        WidgetLogger.pool[name]['logger'].removeHandler(WidgetLogger.WidgetLogHandler(widget))

    @staticmethod
    def detach_all_widgets_from_logger(name: str = GENERAL):
        if name not in WidgetLogger.pool:
            return

        for widget in WidgetLogger.pool[name]['attached_widgets']:
            WidgetLogger.pool[name]['logger'].removeHandler(WidgetLogger.WidgetLogHandler(widget))

        WidgetLogger.pool[name]['attached_widgets'] = []

    @staticmethod
    def set_terminator(terminator: str, logger: logging.Logger):
        for handler in logger.handlers:
            handler.terminator = terminator

    class DebugLogHandler(StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            debug.debug(msg)

    class WidgetLogHandler(StreamHandler):
        def __init__(self, widget):
            super().__init__()
            self.widget = widget

        def emit(self, record):
            msg = self.format(record)
            self.widget.v_model = self.widget.v_model + msg + self.terminator

            debug.run_js("""
                setTimeout(()=>{
                    let elem = document.querySelector('#%s');
                    elem.scrollTo({top:elem.scrollHeight});
                }, 100);
            """ % self.widget.id)
