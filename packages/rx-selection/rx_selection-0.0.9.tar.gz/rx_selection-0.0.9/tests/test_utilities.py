from log_store import log_store 
log=log_store.add_logger(name='selection:test_utilities')

import selection.utilities as slut
import numpy
import math

#------------------------------
def test_transform_bdt():
    log.info('Tranform')
    for bdt in [ 0.1 * val for val in range(-10, 11)]:
        val = slut.transform_bdt(bdt)
        log.debug(f'{bdt:<10.3f}{"->"}{val:>10.3f}')
#------------------------------
def test_inverse_transform_bdt():
    log.info('Inverse tranform')
    for bdt_in in [ 0.1 * val for val in range(-10, 11)]:
        bdt_tr = slut.transform_bdt(bdt_in)
        bdt_or = slut.inverse_transform_bdt(bdt_tr)

        if not math.isclose(bdt_or, bdt_in):
            log.error('BDT scores are different:') 
            log.info(f'{bdt_in:<10.3f}{"->"}{bdt_tr:>10.3f}')
            log.info(f'{bdt_tr:<10.3f}{"<-"}{bdt_or:>10.3f}')
            raise

        log.debug(f'{bdt_in:<10.3f}{"->"}{bdt_tr:>10.3f}')
        log.debug(f'{bdt_tr:<10.3f}{"->"}{bdt_or:>10.3f}')
        log.debug('')
#------------------------------
def main():
    test_transform_bdt()
    test_inverse_transform_bdt()
#------------------------------
if __name__ == '__main__':
    main()


