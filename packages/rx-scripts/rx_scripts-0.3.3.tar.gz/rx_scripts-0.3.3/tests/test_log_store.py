from log_store import log_store

import logzero 

#--------------------------------
def test_simple():
    log_store.set_level('obj_1', logzero.WARNING)
    
    log_1 = log_store.add_logger('obj_1')
    log_2 = log_store.add_logger('obj_2')
    
    log_store.show_loggers()
#--------------------------------
def main():
    test_simple()

if __name__ == '__main__':
    main()

