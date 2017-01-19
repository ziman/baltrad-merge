#!/opt/baltrad/third_party/bin/python
'''
Copyright (C) 2012- Swedish Meteorological and Hydrological Institute (SMHI)

This file is part of RAVE.

RAVE is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RAVE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with RAVE.  If not, see <http://www.gnu.org/licenses/>.
'''

## Compiles SCANs to PVOLs. Will only use the scans located closest to the
#  nominal (reference) time given as an argument.
#  This modules uses multiprocessing to distribute the job among CPU cores.

## @file
## @author Daniel Michelson, SMHI
## @date 2012-01-26

import sys, os, glob, time
import _raveio, _polarvolume
import odim_source
import polar_merger
from Proj import rd


# @param ts string of format YYYYMMDDHHmm
# @returns float seconds since epoch to be used with time.localtime
def GetTime(ts):
    YYYY, MM, DD = int(ts[:4]), int(ts[4:6]), int(ts[6:8])
    HH, mm = int(ts[8:10]), int(ts[10:12])

    return time.mktime((YYYY,MM,DD,HH,mm,0,0,0,0))


## Read a boatload of SCAN files from a single acquitition period and generate
# PVOLs from them, where the data closest to nominal time are chosen.
# This will read ALL data over a 15 min period, ie. 5-minute data, but only
# write a single PVOL for the period. Scan order is preserved only in cases
# where data are acquired ascending or descending, not interleaved.
# Calling this function works just as easily for several radars as it does for
# one, although it is smarter to use multi_generate() to distribute the
# processing load.
# @param args tuple containing the nominal time (in seconds past epoch) and
# a list of file strings containing input data.
def generate(args):
    import rave_pgf_logger
    logger = rave_pgf_logger.rave_pgf_syslog_client()
    seconds, files = args
    ndt = None
    master = {}
    merger = polar_merger.polar_merger(15) # 15 minute interval

    for fstr in files:
        try:
          obj = _raveio.open(fstr).object
        except Exception, e:
          logger.exception("Failed to open file %s"%fstr)
          continue

        src = odim_source.ODIM_Source(obj.source)
        node = src.nod
        angle = round(obj.elangle * rd, 1)

        # If this radar isn't in the dictionary, put it there
        if node not in master.keys():
            master[node] = {}

        # If this elevation angle isn't in the node's list, put it there
        angles = master[node]

        if angle not in angles.keys() and angle < 90.0:
            angles[angle] = []

        if angle < 90.0:
            angles[angle].append(obj)

        if ndt is None:
            ndt = merger.create_nominal_time_str(obj.date, obj.time)

    # We now have a dictionary for each site containing a dictionary of
    # angles, where the scans are. Start organizing them...
    ttuple = time.localtime(seconds)

    #print `ttuple`
    #sys.exit(0)

    for node in master.keys():
        #print 'NODE', node

        pvol = _polarvolume.new()
        pvol.date = ndt[:8] #time.strftime("%Y%m%d", ttuple)  # Nominal time
        pvol.time = ndt[8:] #time.strftime("%H%M%S", ttuple)

        angles = master[node].keys()
        angles.sort()

        dtime = 10e10  # Dummy initial time difference

        # So for each angle
        for angle in angles:
            #print 'ANGLE', angle, len(master[node][angle])

            scan2add = None  # Very important marker
            lon, lat, height = None, None, None

            # Loop through the list of scans, determine the one closest to
            # nominal time
            for scan in master[node][angle]:
                lon = float(scan.longitude)
                lat = float(scan.latitude)
                height = float(scan.height)
                DATE, TIME = scan.startdate, scan.starttime
                scansecs = GetTime(DATE+TIME[:-2])
                dthis = scansecs - seconds

                # Sanity check for French (and other?) data
                if (scan.nbins * scan.rscale / 1000) < scan.rstart:
                    scan.rstart /= 1000.0

                if dthis <= dtime or scan2add == None:
                    dtime = dthis
                    scan2add = scan

            pvol.addScan(scan2add)
            #print "%s %2.1f %s" % (scan2add.starttime,
            #                       scan2add.elangle * rd, scan2add.source)

        pvol.latitude = lat
        pvol.longitude = lon
        pvol.height = height
        pvol.beamwidth = scan2add.beamwidth
        pvol.source = scan.source

        # For the purists, was this volume collected ascending or descending?
        # This is tricker for interleaved scan strategies...
        nrscans = pvol.getNumberOfScans()
        first, last = pvol.getScan(0), pvol.getScan(nrscans-1)
        if int(first.starttime) > int(last.starttime):
            pvol.sortByElevations(0)

        rio = _raveio.new()
        rio.object = pvol
        rio.filename = 'polar_filename.h5'
        rio.save()
    return rio.filename  # Only really useful with data from one radar


## Distributes 'generate' among the available CPU cores on this machine.
#  @param seconds float representing seconds past the epoch
def multi_generate(seconds=None):
    import datetime
    import multiprocessing

    pool = multiprocessing.Pool(8)
    seconds = 0
    path = '.'

    files = glob.glob(os.path.join(path, '*scan*.h5'))
    nodes, args = [], []
    for fstr in files:
        print('FSTR',fstr)
        node = os.path.split(fstr)[1][:5]
        if node not in nodes:
            nodes.append(node)
            nodefiles = glob.glob(os.path.join(path, node+'*scan*.h5'))
            args.append((seconds,nodefiles))

    print('ARGS', args)
    results = []
    r = pool.map_async(generate, args, chunksize=1, callback=results.append)
    r.wait() # Wait on the results
#    for i in range(len(results[0])):
#        print nodes[i], results[0][i]
    return len(files), results[0]


if __name__ == "__main__":
    done = multi_generate()



