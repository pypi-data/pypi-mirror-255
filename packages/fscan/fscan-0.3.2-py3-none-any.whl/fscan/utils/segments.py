# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Evan Goetz (2023)
#
# This file is part of fscan

import math
import numpy as np
import os
from dqsegdb2.query import query_segments
from ligo.segments import segment, segmentlist, segmentlistdict
from gwdatafind import find_urls


def find_segments(epseg_info, intersect_data=False):
    """
    This queries the segment database for the specified segment type.

    By default, this will query <ifo>:DMT-ANALYSIS_READY.
    If a segment file (or ALL) is given, then just copy over the segement
    file specified to the SFTpath / epoch directory
    """
    SFTGPSstart = epseg_info['GPSstart']  # initial value, may be amended later
    GPSend = epseg_info['GPSstart'] + epseg_info['duration']
    step = epseg_info['Tsft'] * (1 - epseg_info['overlap_fraction'])

    # If there's already a segment file, we don't need to make one.
    # We'll just read from it (at the end of this function) to make
    # sure the correct start and end times are recorded.
    if os.path.exists(epseg_info['segfile']):
        pass

    else:
        if epseg_info['segtype'] == ['ALL']:
            print("Using all available data with no segment type restriction")
            segs = segmentlist([segment(epseg_info['GPSstart'], GPSend)])

        # If no segment file given, and segment type isn't 'ALL',
        # then query the segment database
        else:
            print("Querying segments")
            segdict = segmentlistdict()
            for segtype in epseg_info['segtype']:
                segdict[segtype] = query_segments(
                    segtype,
                    epseg_info['GPSstart'],
                    GPSend)['active']
            segs = segdict.intersection(epseg_info['segtype'])
            if len(segs) == 0:
                return None, None
            # If the earliest segment goes all the way to the starting
            # cutoff point, step back 1 day. We are looking for the point
            # where the flag actually became active
            lookback_window = 24*60*60  # TODO: handle this more intelligently
            if segs[0][0] <= epseg_info['GPSstart']:
                prev_epoch_segs = query_segments(
                    segtype,
                    epseg_info['GPSstart'] - lookback_window,
                    epseg_info['GPSstart'],
                    coalesce=True)['active']

                prev_epoch_segstart = int(prev_epoch_segs[-1][0])

                # Align the segments to an integer multiple of 'step'
                # counting from the the point where the flag became active
                SFTGPSstart = (
                    epseg_info['GPSstart'] +
                    (step - (epseg_info['GPSstart'] - prev_epoch_segstart) %
                     step))
                SFTGPSstart = int(SFTGPSstart)
                print(f"Aligning segments to a new start time: {SFTGPSstart}")

        # If requested, here we find the data first and check if it is
        # available and intersect with the requested segments
        if intersect_data:
            for idx, frametype in enumerate(epseg_info['frametypes']):
                # query for the data of this frametype, spit out a warning if
                # some data is not available
                urls = find_urls(frametype[0], frametype, SFTGPSstart, GPSend,
                                 on_missing='warn')

                # create a segment list from each of the frame files
                data_segs = segmentlist()
                for n, url in enumerate(urls):
                    filedata = os.path.splitext(
                        os.path.basename(url))[0].split('-')
                    filestart = int(filedata[-2])
                    fileend = filestart + int(filedata[-1])
                    data_segs.append(segment(filestart, fileend))

                # merge (coalesce) the data file segments
                data_segs.coalesce()

                # intersect with segs
                segs &= data_segs

        os.makedirs(epseg_info['epoch_path'], exist_ok=True)
        with open(epseg_info['segfile'], 'w') as f:
            for seg in segs:

                # This is done for 2 reasons:
                # (a) because dqsegdb2 has historically returned
                # GPS times outside the range requested, and (b)
                # because the SFTGPSstart is adjusted (possibly moved
                # later) relative to the GPSstart that was initially
                # used to query the segments.
                if int(seg[0]) < SFTGPSstart:
                    seg = segment(SFTGPSstart, seg[1])

                # This is just compensating for the dqsegdb2 issue
                # described above
                if int(seg[1]) > GPSend:
                    seg = segment(seg[0], GPSend)

                # This is because any extra time around the SFTs will
                # cause lalpulsar_MakeSFTDAG to "center" the SFTs in a
                # way that causes inconsistencies between avg durations
                nsteps = int(math.floor((seg[1] - seg[0]) / step))
                seg = segment(seg[0], seg[0] + nsteps * step)

                # write this segment to the segment file
                f.write(f"{int(seg[0])} {int(seg[1])}\n")

    # Read from the segment file to return the updated start and
    # end GPS (this will be necessary to correctly name plots and
    # configure summary pages).
    # Note: we do this whether the segment file was just generated
    # or created earlier.
    segdat = np.genfromtxt(epseg_info['segfile'], dtype='int')
    if len(segdat) == 0:
        return None, None
    else:
        segdat = np.atleast_2d(segdat)
        return segdat[0][0], segdat[-1][-1]
