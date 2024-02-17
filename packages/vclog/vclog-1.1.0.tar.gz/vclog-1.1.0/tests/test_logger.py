import time
from vclog import Logger


def main():
    before = time.time()

    # Instance logging
    logger_pepe = Logger('pacopepekatanas')

    Logger.plain("\nPrinting with instanced logger")
    logger_pepe.info('info')
    logger_pepe.debug('debug')
    logger_pepe.warning('warning')
    logger_pepe.error('error')
    Logger.plain('%%%%%%%%%')

    # Static logging
    Logger.plain("\nPrinting with static logger")
    Logger.info('info')
    Logger.debug('debug')
    Logger.warning('warning')
    Logger.error('error')
    Logger.plain('%%%%%%%%%')

    # Miscellaneous
    logger_cgp: Logger = Logger('cgp')
    logger_cgp.info('training model')

    logger_data: Logger = Logger('data_manager')
    logger_data.info('dataset generated')

    Logger.plain('%%%%%%%%%')
    logger_pepe.error('pepe')
    logger_data.debug('data')
    logger_cgp.warning('cgp')

    Logger.debug(Logger.__qualname__)

    # Plain mode
    logger_plain: Logger = Logger('plain')

    Logger.plain('green', color='green')
    Logger.plain('red', color='red')
    Logger.plain('blue', color='blue')
    Logger.plain('yellow', color='yellow')
    Logger.plain('magenta', color='magenta')
    Logger.plain('cyan', color='cyan')
    Logger.plain('white', color='white')
    Logger.plain('secondary_green', color='secondary_green')
    Logger.plain('secondary_red', color='secondary_red')
    Logger.plain('secondary_blue', color='secondary_blue')
    Logger.plain('secondary_yellow', color='secondary_yellow')
    Logger.plain('secondary_magenta', color='secondary_magenta')
    Logger.plain('secondary_cyan', color='secondary_cyan')
    Logger.plain('secondary_white', color='secondary_white')

    Logger.plain('%%%%%%%%%')

    Logger.plain('bold', style='bold')
    Logger.plain('dim', style='dim')
    Logger.plain('italic', style='italic')
    Logger.plain('underline', style='underline')
    Logger.plain('blink', style='blink')
    Logger.plain('highlight', style='highlight')
    Logger.plain('hidden', style='hidden')
    Logger.plain('strikethrough', style='strikethrough')
    Logger.plain('double_underline', style='double_underline')

    Logger.plain('%%%%%%%%%')

    Logger.plain('green_bg', bg_color='green')
    Logger.plain('red_bg', bg_color='red')
    Logger.plain('blue_bg', bg_color='blue')
    Logger.plain('yellow_bg', bg_color='yellow')
    Logger.plain('magenta_bg', bg_color='magenta')
    Logger.plain('cyan_bg', bg_color='cyan')
    Logger.plain('white_bg', bg_color='white')
    Logger.plain('secondary_green_bg', bg_color='secondary_green')
    Logger.plain('secondary_red_bg', bg_color='secondary_red')
    Logger.plain('secondary_blue_bg', bg_color='secondary_blue')
    Logger.plain('secondary_yellow_bg', bg_color='secondary_yellow')
    Logger.plain('secondary_magenta_bg', bg_color='secondary_magenta')
    Logger.plain('secondary_cyan_bg', bg_color='secondary_cyan')
    Logger.plain('secondary_white_bg', bg_color='secondary_white')

    Logger.plain('%%%%%%%%%')

    Logger.plain('green', color='green', style='bold')
    Logger.plain('red', color='red', style='underline')
    Logger.plain('blue', color='blue', style='blink')
    Logger.plain('yellow', color='yellow', style='italic')
    Logger.plain('magenta', color='magenta', style='highlight')
    Logger.plain('cyan', color='cyan', style='hidden')
    Logger.plain('white', color='white', style='strikethrough')
    Logger.plain('secondary_green', color='secondary_green', style='double_underline')
    Logger.plain('secondary_red', color='secondary_red', style='bold')
    Logger.plain('secondary_blue', color='secondary_blue', style='underline')
    Logger.plain('secondary_yellow', color='secondary_yellow', style='blink')
    Logger.plain('secondary_magenta', color='secondary_magenta', style='italic')
    Logger.plain('secondary_cyan', color='secondary_cyan', style='highlight')
    Logger.plain('secondary_white', color='secondary_white', style='hidden')

    Logger.plain('%%%%%%%%%')

    Logger.plain('green', color='green', bg_color='blue')
    Logger.plain('red', color='red', bg_color='yellow')
    Logger.plain('blue', color='blue', bg_color='green')
    Logger.plain('yellow', color='yellow', bg_color='red')
    Logger.plain('magenta', color='magenta', bg_color='white')
    Logger.plain('cyan', color='cyan', bg_color='secondary_white')
    Logger.plain('white', color='white', bg_color='cyan')
    Logger.plain('secondary_green', color='secondary_green', bg_color='secondary_white')
    Logger.plain('secondary_red', color='secondary_red', bg_color='secondary_cyan')
    Logger.plain('secondary_blue', color='secondary_blue', bg_color='secondary_magenta')
    Logger.plain('secondary_yellow', color='secondary_yellow', bg_color='secondary_red')
    Logger.plain('secondary_magenta', color='secondary_magenta', bg_color='secondary_yellow')
    Logger.plain('secondary_cyan', color='secondary_cyan', bg_color='secondary_blue')
    Logger.plain('secondary_white', color='secondary_white', bg_color='secondary_green')

    Logger.plain('%%%%%%%%%')

    Logger.plain('green', color='green', bg_color='blue', style='bold')
    Logger.plain('red', color='red', bg_color='yellow', style='underline')
    Logger.plain('blue', color='blue', bg_color='green', style='blink')
    Logger.plain('yellow', color='yellow', bg_color='red', style='italic')
    Logger.plain('magenta', color='magenta', bg_color='white', style='highlight')
    Logger.plain('cyan', color='cyan', bg_color='secondary_white', style='hidden')
    Logger.plain('white', color='white', bg_color='cyan', style='strikethrough')
    Logger.plain('secondary_green', color='secondary_green', bg_color='secondary_white', style='double_underline')
    Logger.plain('secondary_red', color='secondary_red', bg_color='secondary_cyan', style='bold')
    Logger.plain('secondary_blue', color='secondary_blue', bg_color='secondary_magenta', style='underline')
    Logger.plain('secondary_yellow', color='secondary_yellow', bg_color='secondary_red', style='blink')
    Logger.plain('secondary_magenta', color='secondary_magenta', bg_color='secondary_yellow', style='italic')
    logger_plain.plain('secondary_cyan', color='secondary_cyan', bg_color='secondary_blue', style='highlight')
    logger_plain.plain('secondary_white', color='secondary_white', bg_color='secondary_green', style='hidden')

    Logger.plain('%%%%%%%%%')

    Logger.plain('green', color='green', style=['bold', 'underline', 'blink', 'italic', 'strikethrough', 'double_underline'])

    after = time.time()

    print(f'Elapsed time: {(after - before)*1000:.2f} ms')

    flush_logger = Logger('flush')
    for i in range(100):
        flush_logger.error(f"flushing: {i}%", flush=True)
        time.sleep(0.1)


if __name__ == '__main__':
    main()
