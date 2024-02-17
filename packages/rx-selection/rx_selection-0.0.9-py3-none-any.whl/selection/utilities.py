import math 

from log_store      import log_store

log=log_store.add_logger(name='selection:utilities')
#-------------------------------------
def transform_bdt(working_point):
    '''
    Will return BDT score after using RK central analysis' transformation

    Parameters
    ------------
    working_point (float): Working point from TMVA, from -1 to 1

    Returns 
    ------------
    working_point (float): Working point transformed, from 0 to 1 + epsilon  
    '''
    if not isinstance(working_point, float):
        log.error(f'Working point is not a float, but: {type(working_point)}={working_point}')
        raise

    try:
        a = math.asin(working_point) * (2. / math.pi)
        b = (math.asin(a) + 0.5 * math.pi) / 3.
    except:
        log.error(f'Cannot transform score at: {working_point}')
        raise

    return b 
#-------------------------------------
def inverse_transform_bdt(working_point):
    if not isinstance(working_point, float):
        log.error(f'Working point is not a float, but: {type(working_point)}={working_point}')
        raise

    a=math.sin(3 * working_point - 0.5 * math.pi)
    w=math.sin(a * math.pi / 2.)

    return w
#-------------------------------------

