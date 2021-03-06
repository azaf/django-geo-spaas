"""Note: This is tested on Sentinel-1 and Sentinel-2 data from the Norwegian ground segment, and
Arome forecasts from thredds.met.no. Other repositories may require slight changes in the code. This
must be developed gradually..
"""
import warnings
from thredds_crawler.crawl import Crawl

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from geospaas.utils.utils import validate_uri
from geospaas.catalog.models import DatasetURI
from geospaas.nansat_ingestor.models import Dataset as NansatDataset

def crawl(url, **options):
    validate_uri(url)

    date = options.get('date', None)
    filename = options.get('filename', None)
    if date:
        select = ['(.*%s.*\.nc)' %date]
    elif filename:
        select = ['(.*%s)' %filename]
    else:
        select = None

    skips = Crawl.SKIPS + ['.*ncml']
    c = Crawl(url, select=select, skip=skips, debug=True)
    added = 0
    for ds in c.datasets:
        url = [s.get('url') for s in ds.services if
                s.get('service').lower()=='opendap'][0]
        try:
            gds, cr = NansatDataset.objects.get_or_create(url)
        except (IOError, AttributeError) as e:
            #warnings.warn(e.message)
            continue
        else:
            if cr:
                added += 1
                print('Added %s, no. %d/%d'%(url, added, len(c.datasets)))
        # Connect all service uris to the dataset
        for s in ds.services:
            try:
                ds_uri, _ = DatasetURI.objects.get_or_create(name=s.get('name'),
                    service=s.get('service'), uri=s.get('url'), dataset=gds)
            except IntegrityError:
                # There is no standard for the name (and possibly the service). This means that the
                # naming defined by geospaas.catalog.managers.DAP_SERVICE_NAME (and assigned to the
                # DatasetURI in geospaas.nansat_ingestor.managers.DatasetManager.get_or_create) may
                # be different from s.get('name').
                # Solution: ignore the error and continue the loop
                continue
    return added

class Command(BaseCommand):
    args = '<url> <select>'
    help = """
        Add metadata of datasets available on thredds/opendap to archive. 

        Args:
            <url>: the url to the thredds catalog
            <date>: Select datasets by date (yyyy/mm/dd)
            <filename>: Select datasets by filename

        Example: 
            (1) Find all Sentinel-2A datasets in 2017

            url = 'http://nbstds.met.no/thredds/catalog/NBS/S2A/catalog.html'
            date = '2017/01/10'

            (2) Find a specific file

            url = 'http://nbstds.met.no/thredds/catalog/NBS/S2A/catalog.html'
            filename = 'S2A_MSIL1C_20170201T111301_N0204_R137_T32WNS_20170201T111255.nc'
        """

    def add_arguments(self, parser):
        parser.add_argument('url', nargs='*', type=str)
        parser.add_argument('--date',
                            action='store',
                            default='',
                            help='''Date of coverage (yyyy/mm/dd)''')
        parser.add_argument('--filename',
                            action='store',
                            default='',
                            help='''Filename of a specific dataset''')

    def handle(self, *args, **options):
        if not len(options['url'])==1:
            raise IOError('Please provide a url to the data')
        url = options.pop('url')[0]
        added = crawl(url, **options)
        self.stdout.write(
            'Successfully added metadata of %s datasets' %added)
