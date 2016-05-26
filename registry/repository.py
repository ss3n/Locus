from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Region

__author__ = 'udaymittal'

# create postgres engine
engine = create_engine('postgresql://udaymittal:root@localhost/locus')
Session = sessionmaker(bind=engine)
session = Session()

def get_region_name(longitude, latitude):
    '''
        Function to get the region name given a point
    :param latitude: point's latitude
    :param longitude: point's longitude
    :return:
    '''
    point = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
    query = session.query(Region).filter(func.ST_Contains(Region.regionboundary, point)).first()
    return query.name

