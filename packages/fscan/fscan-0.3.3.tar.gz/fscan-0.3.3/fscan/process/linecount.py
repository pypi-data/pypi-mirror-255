# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#
# This file is part of fscan

import matplotlib as mpl
from matplotlib import pyplot as plt
import os
from ..utils import dtutils as dtl
import argparse
import glob
import numpy as np
from scipy import stats
from email.message import EmailMessage
import socket
import smtplib
from ..utils.utils import str_to_bool
mpl.use('Agg')


def get_all_epoch_spects(targetPath, minEpochs, maxEpochs):
    '''
    For the given target folder and min/max number of epochs,
    return all the spectra found and their associated timestamps.

    Parameters
    ----------
    target : string
        The target or 'current' directory, corresponding to the
        end point of the time span that should be analyzed.

    minEpochs : int
        The minimum number of epochs (e.g. days) that should be
        analyzed. If not enough data can be found to meet this
        criterion, an exception will be raised.

    maxEpochs : int
        The maximum number of epochs (e.g. days) that should be
        analyzed. Determines the total number of directories that
        will be searched for spectrum files

    Returns
    -------
    timeTags : list of strings
        For each spectrum located, this list contains a string
        labeling the day (or other epoch timestamp). Example:
        ["20200201","20200202","20200204"]

    foundSpects : list of strings
        For each spectrum located, this list contains a file path
        to the actual data file. Data files are expected to start
        with 'fullspect_' and end with '_timeaverage.npz'
    '''

    # Handle the file paths to extract strings indicating the
    # timestamp and the averaging duration
    targetPath = os.path.abspath(targetPath)
    epochPath, channelTag = os.path.split(targetPath)
    avgDurPath, timeStampStr = os.path.split(epochPath)
    parentDir, avgDurStr = os.path.split(avgDurPath)

    # temporary fix that turns "day" string into "1day" for parsing
    # by utils.datetime module.
    # (this should be fixed more neatly in recent merge request - MR30)
    if not avgDurStr[0].isnumeric():
        dtlAvgDurStr = "1"+avgDurStr
    else:
        dtlAvgDurStr = avgDurStr

    # convert the information to datetime and timedelta formats
    timeStamp = dtl.datestr_to_datetime(timeStampStr)
    avgDur, _ = dtl.deltastr_to_timedelta(dtlAvgDurStr)

    # set up arguments to feed to utils.datetime
    dtlArgs = argparse.Namespace()
    dtlArgs.analysisEnd = timeStampStr
    dtlArgs.analysisStart = (timeStamp - maxEpochs*avgDur).strftime(
        "%Y-%m-%d-%H:%M:%S")
    dtlArgs.averageDuration = dtlAvgDurStr
    dtlArgs.analysisDuration = None  # utils.datetime will handle this
    dtlArgs.snapToLast = ''  # we don't care about snapping for this use case
    dtlArgs.greedy = False

    # obtain the directories we will need to search
    _, _, epochtags = dtl.args_to_intervals(dtlArgs)
    if timeStampStr not in epochtags:
        epochtags += [timeStampStr]
    searchPaths = [
        os.path.join(parentDir, avgDurStr, tag) for tag in epochtags]

    # search for directories that contain "spec_*" type files ending in numbers
    foundSpects = []
    timeTags = []
    for p in searchPaths:
        searchPattern = os.path.join(
            p, channelTag, "fullspect_*_timeaverage.npz")
        matchFiles = glob.glob(searchPattern)
        if len(matchFiles) > 1:
            raise Exception("More than one merged spectrum file was found "
                            f"using this pattern: {searchPattern}")
        elif len(matchFiles) == 1:
            foundSpects += matchFiles
            _, timeTag = os.path.split(p)
            timeTags += [timeTag]
        else:
            pass

    foundPrint = "\n".join(foundSpects)

    # Check that all the files have the same frequency range
    fnames = [os.path.basename(f) for f in foundSpects]
    bandTags = ["_".join(name.split("_")[1:3]) for name in fnames]
    if len(set(bandTags)) > 1:
        raise Exception("The frequency band is not the same within the "
                        "folders found. Here are the files: \n"
                        f"{foundPrint}")

    return timeTags, foundSpects


def alert_cutoff(line_counts):
    '''
    We want to send an alert if the current ("target") line count,
    located at the end of the list of line_counts, exceeds the
    historical mean + 2 times the historical standard deviation.

    This function calculates the cutoff from line_count.

    Parameters
    ----------
    line_counts : list of ints
        Line counts in chronological order.

    Returns
    -------
    cutoff : float
    '''
    mean, std = historical_stats(line_counts)
    return mean + 2*std


def historical_stats(line_counts):

    mean = np.average(line_counts[:-1])
    std = np.std(line_counts[:-1])

    return mean, std


def create_history_plot(timeTags, line_counts, targetPath, minEpochs):
    '''
    Creates a scatter plot of the number of line counts vs time
    which is saved in the targetPath directory.
    Returns the path to the generated plot.

    Parameters
    ----------
    timeTags : list of strings
        For example, ["20200201","20200202","20200204"]

    line_counts : list of ints
        Line counts in chronological order

    targetPath : string
        The target or 'current' directory, corresponding to the
        end point of the time span that should be analyzed.

    Returns
    -------
    plotname : string
        Path to generated plot
    '''

    targetPath = os.path.abspath(targetPath)
    plotname = os.path.join(targetPath, "line_count_history.png")
    plt.clf()
    colors = np.array(['deepskyblue']*len(line_counts))
    edgecolors = np.array(['none']*len(line_counts), dtype=str)
    if len(edgecolors) > 1:
        edgecolors[-1] = '0000'
    if len(line_counts) >= minEpochs:
        alertc = alert_cutoff(line_counts)
        above = np.where(line_counts >= alertc)[0]
        colors[above] = 'coral'
        plt.scatter(timeTags,
                    line_counts,
                    marker='o',
                    zorder=5,
                    color=colors,
                    edgecolors=edgecolors,
                    linewidth=2)
        plt.axhline(alertc,
                    label="Alert threshold",
                    color='orangered',
                    linewidth=3)
        mean, std = historical_stats(line_counts)
        hvals = [mean+std, mean, mean-std]
        hlabs = ["mean + stddev", "mean", "mean - stddev"]
        cols = ['orange', 'lightblue', 'lightgreen']
        for hval, hlab, col in zip(hvals, hlabs, cols):
            plt.axhline(hval, label=hlab,
                        zorder=1,
                        color=col,
                        linestyle=":")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.title("Line count over time")
    else:
        plt.scatter(timeTags,
                    line_counts,
                    zorder=5,
                    color=colors,
                    edgecolors=edgecolors,
                    linewidth=2)
        plt.title("Line count over time\n[Note: not enough data to "
                  "calculate statistics.]")
    plt.xticks(rotation=-90)
    plt.xlabel("Date")
    plt.ylabel("Number of lines")
    plt.tight_layout()
    plt.savefig(plotname)
    return plotname


def create_histogram(line_counts, targetPath):
    '''
    Creates a histogram of historical line counts
    which is saved in the targetPath directory.
    Returns the path to the generated plot.

    Parameters
    ----------
    line_counts : list of ints
        Line counts in chronological order

    targetPath : string
        The target or 'current' directory, corresponding to the
        end point of the time span that should be analyzed.

    Returns
    -------
    plotname : string
        Path to generated plot
    '''

    targetPath = os.path.abspath(targetPath)
    plotname = os.path.join(targetPath, "line_count_histogram.png")
    plt.clf()
    plt.hist(line_counts)
    plt.axvline(line_counts[-1], color='orange', label="Today's count")
    plt.xlabel("Number of lines")
    plt.ylabel("Number of days occurring")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plotname)
    return plotname


def get_url(targetPath):
    '''
    If the target path is in a public_html directory, this function will
    attempt to turn it into a URL that can be accessed from the web.

    Parameters
    ----------
    targetPath : string
        The target or 'current' directory, corresponding to the
        end point of the time span that should be analyzed.

    Returns
    -------
    url : string
        Url to access the targetPath via the web.
        Alternatively, return `None` if `targetPath` is not
        in a `public_html` directory
    '''
    targetPath = os.path.abspath(targetPath)
    if "public_html" in targetPath:
        hname = socket.getfqdn()
        cltag = None
        for cltag_opt in ['ligo', 'ligo-wa', 'ligo-la']:
            if f".{cltag_opt}.caltech.edu" in hname:
                cltag = cltag_opt
                break
        uname = targetPath.split("/home/")[1].split("/public_html")[0]
        url = targetPath.replace(
            f"/home/{uname}/public_html",
            f"https://ldas-jobs.{cltag}.caltech.edu/~{uname}"
            )
        return url
    else:
        return None


def send_email(addressFrom, addressTo, url, historyUrl, histogramUrl):
    '''
    As it says on the tin - send an email. The email should contain
    links (or, if they are not in a `public_html` directory, just paths)
    to the directory that triggered the alert and the corresponding paths.

    Parameters
    ----------
        addressFrom : string
        addressTo : string
        url : string
            URL for main folder
        historyUrl : string
            URL to history plot
        histogramUrl : string
            URL to histogram plot

    '''

    msg = EmailMessage()
    msg['Subject'] = ('Line count detected above threshold by Forest of Lines '
                      'monitor')
    msg['From'] = [addressFrom]
    msg['To'] = [addressTo]
    msgContent = "\n".join([
        f"Data can be found here: {url}",
        f"Line history plot: {historyUrl}",
        f"Line histogram plot: {histogramUrl}"
        ])
    msg.set_content(msgContent)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def generate_line_count(spect, cutoff, fmax):
    '''
    For a given spectrum file (.npz) and a cutoff value,
    determine the number of lines.

    Parameters
    ----------
    spect : string
        Path to an .npz spectrum file

    cutoff : float
        Probability cutoff value to be converted to a threshold.
        Spectral bins above the threshold (less probable) will be
        counted as lines.

    Returns
    -------
    numLines : int
        Number of lines (number of bins above threshold)
    '''

    print(f"generating line count for {spect}")
    data = np.load(spect)
    f = data['f']
    vals = data['normpow']
    vals = vals[f <= fmax]

    channelPath, _ = os.path.split(spect)
    numSFTs = len(glob.glob(os.path.join(channelPath, "sfts/*")))
    deg_freedom = numSFTs*2
    cutoff = float(stats.chi2.isf(cutoff, deg_freedom)) / float(deg_freedom)
    numLines = len(vals[vals > cutoff])
    return numLines


def extract_line_count(spects, probCut, fmax, regenerate=False):
    '''
    Read the previously generated line counts from a file. If the file
    does not exist, generate it instead.

    Parameters
    ----------
    spects : list of strings
        List of all spectra to process (.npz files)

    regenerate : bool
        If true, regenerate and overwrite all the line files.

    Returns
    -------
        line_count_list : list of ints
            Line counts for every item in `spects`
    '''
    line_count_list = []
    for spect in spects:
        channelPath, spectFile = os.path.split(spect)
        searchPattern = os.path.join(channelPath, "line_count_*.txt")
        matchFiles = glob.glob(searchPattern)
        if len(matchFiles) > 1:
            raise Exception("More than one line count file was found with "
                            f"pattern: {searchPattern}")
        if len(matchFiles) == 0 or regenerate:
            line_count = generate_line_count(spect, probCut, fmax)
            outfile = os.path.join(
                channelPath, f"line_count_{spectFile.replace('.npz', '.txt')}")
            with open(outfile, 'w') as f:
                f.write(str(line_count))
        else:
            with open(matchFiles[0], "r") as file_in:
                print(f"Reading from {matchFiles[0]}")
                lines = file_in.readlines()
                if len(lines) == 1:
                    line_count = int(lines[0])
                else:
                    line_count = generate_line_count(spect, probCut, fmax)
        line_count_list += [line_count]
    return line_count_list


def runForestOfLines(targetDir, minEpochs, maxEpochs,
                     probCut=1e-6, fmax=100,
                     emailFrom=None, emailTo=None, overwrite=False):

    '''
    This is the main function which runs the others. In short, it locates all
    the needed directories, extracts or generates the line counts, and sends
    an email if specified by the user and if the current line count is over
    the alert threshold (determined by previous days).
    '''
    timeTags, spects = get_all_epoch_spects(targetDir, minEpochs, maxEpochs)
    line_counts = extract_line_count(spects, probCut, fmax, overwrite)

    history_plot_path = create_history_plot(timeTags, line_counts,
                                            targetDir, minEpochs)
    histogram_plot_path = create_histogram(line_counts, targetDir)
    mainUrl = get_url(targetDir)
    historyUrl = get_url(history_plot_path)
    histogramUrl = get_url(histogram_plot_path)

    if len(line_counts) >= minEpochs:
        if (emailFrom and emailTo and
                line_counts[-1] > alert_cutoff(line_counts)):
            if mainUrl and historyUrl and histogramUrl:
                send_email(emailFrom,
                           emailTo,
                           mainUrl,
                           historyUrl,
                           histogramUrl)
            else:
                send_email(emailFrom,
                           emailTo,
                           targetDir,
                           history_plot_path,
                           histogram_plot_path)


if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser()
    parser.register('type', 'bool', str_to_bool)

    # Set up the user arguments
    parser.add_argument("--targetDirectory", type=str,
                        help="Directory to analyze in context of historical "
                             "data. Path should take the form [parent_dir]/"
                             "Tsft/segment-type/avg-duration/timestamp.")
    parser.add_argument("--maxEpochs", type=int, default=30,
                        help="Maximum number of epochs (e.g. days) to count "
                             "backward for historical data.")
    parser.add_argument("--minEpochs", type=int, default=5,
                        help="Minimum number of epochs (e.g. days) to count "
                             "backward for historical data.")
    parser.add_argument("--overwriteLineCounts", type='bool',
                        help="If true, regenerate line counts for prior "
                             "epochs.")
    parser.add_argument("--emailFrom", type=str, default=None,
                        help="Sender email address for alerts")
    parser.add_argument("--emailTo", type=str, default=None,
                        help="Recipient email address for alerts")
    parser.add_argument("--lineProbCutoff", type=float, default=1e-6,
                        help="The chi-square tail cumulative probability used "
                             "to define loud lines")
    parser.add_argument("--fmax", type=float, default=100,
                        help="Max frequency for line counting.")
    args = parser.parse_args()

    runForestOfLines(
        args.targetDirectory,
        args.minEpochs,
        args.maxEpochs,
        args.lineProbCutoff,
        args.fmax,
        args.emailFrom,
        args.emailTo,
        args.overwriteLineCounts)
