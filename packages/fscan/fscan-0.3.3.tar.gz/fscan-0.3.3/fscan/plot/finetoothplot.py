# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#
# This file is part of fscan

import numpy as np
import argparse
import itertools
from ..process import spectlinetools as slt
from ..process import linefinder
from ..utils import io
from ..utils.utils import str_to_bool
import bokeh.plotting as bp
import bokeh.models as bm
import bokeh.layouts as bl
import bokeh.events as be


def get_args():
    '''
    Parameters
    ----------
    none

    Returns
    -------
    namespace: parsed arguments
    '''
    parser = argparse.ArgumentParser(
        description="FineTooth plotting tool"
    )

    parser.register('type', 'bool', str_to_bool)

    parser.add_argument(
        "--annotate", type='bool', default=True,
        help=(
            "Allow annotation of plot (default: True). Turn off annotation to"
            " make the plot more lightweight in the browser."))

    parser.add_argument(
        "--spectfile", type=str,
        help="Path to spectrum file. Supports fscan-style npz.")

    parser.add_argument(
        "--freqcolname", type=str, default=None,
        help=(
            "If loading from an npz file, this is the name/key"
            " of the array from which to load frequencies."))

    parser.add_argument(
        "--datacolname", type=str, default=None,
        help=(
            "If loading from an npz file, this is the name/key of the"
            " array from which to load values"))

    parser.add_argument(
        "--ylog", type='bool', default=True,
        help=("Whether to have the y-axis on a log scale"))

    parser.add_argument(
        "--linesfile", type=str, default=None, help="Path to lines file")

    parser.add_argument(
        "--colorcode", type=str,
        choices=['autocolor', 'highlight', 'none'], default=None,
        help=(
            "Autocolor will assign the N most common line descriptions to a"
            " unique dot color (ignores notes in parentheses). Highlight will"
            " assign the N most common tags, indicated by \"!tag\" at the end"
            " of the description, to a unique dot color."))

    parser.add_argument(
        "--colorcode-group-min",
        type=int, default=2,
        help="Minimum number of items in a color-coded group")

    parser.add_argument(
        "--outfile",
        type=str,
        help="Path to output file (must end in .html)")

    parser.add_argument(
        "--title",
        type=str, default=None,
        help="Title for plot")

    parser.add_argument(
        "--yaxlabel",
        type=str, default="ASD",
        help="Y-axis label (default: ASD)")

    parser.add_argument(
        "--fmin",
        type=float, default=-1,
        help="Minimum frequency to display")

    parser.add_argument(
        "--fmax",
        type=float, default=-1,
        help="Maximum frequency to display")

    parser.add_argument(
        "--plotcombs",
        nargs="+",
        type=str,
        default=None,
        help=(
            "Combs to plot on top of other annotations. Must be specified as"
            " \"spacing,offset\". Any line file color coding options will be"
            " overriden so that (up to 8) combs can be color coded."))

    parser.add_argument(
        "--consecpeaks",
        type=int, default=None,
        help="Plot only n number of consecutive peaks fed from plotcombs")

    parser.add_argument(
        "--intersect-linefinder",
        type='bool',
        help=(
            "Whether or not to require that input lines also pass linefinder"
            " thresholds to be plotted"))

    parser.add_argument(
        "--peaksensitivity",
        type=float, default=.001,
        help="(Very approximate) false alarm rate for peak finding")

    parser.add_argument(
        "--peakmedwindow",
        type=float, default=0.05,
        help="spectrum chunk length for calculating running statistics (Hz)")

    parser.add_argument(
        "--legend",
        type='bool', default=False,
        help="Whether a legend should be added to the figure")

    return parser.parse_args()


def plot_spect(outfile, freq, val, title, yaxlabel, ylog):
    ''' Create a basic spectrum plot.

    Parameters
    ----------
    outfile: str
        The output file.
    freq: 1d numpy array
        Frequencies for the spectrum
    val: 1d numpy array
        Values (e.g. ASD, PSD...) for the spectrum
    title: str
        Title for plot
    yaxlabel: str
        y-axis label for plot

    Returns
    -------
        fig: bokeh figure
            The figure on which the spectrum is plotted.
        spectsource: bokeh column data source
            Contains freq, val in a data source.
        spinners: list of bokeh.models Spinner objects
            Used to adjust fmin, fmax, visual reference line, ymin, and ymax.
    '''

    # Set the output file
    bp.output_file(outfile)

    # Spectrum data source
    spectsource = bp.ColumnDataSource({
        'freq': freq,
        'val': val
    })

    if ylog:
        yscale = 'log'
    else:
        yscale = 'linear'
    # Figure for plotting the spectrum
    fig = bp.figure(
        title="Untitled",  # Default plot title
        x_axis_label="Frequency (Hz)",
        y_axis_label=yaxlabel,
        y_axis_type=yscale,
        tools='pan,box_zoom,undo,redo,reset,zoom_in,zoom_out',
        min_width=1500,
    )

    # Add spinners for detailed adjustment of frequency range
    spinner_fmin = bm.Spinner(
        title="Plot min frequency",
        format='0.00000'
    )

    spinner_fmax = bm.Spinner(
        title="Plot max frequency",
        format='0.00000'
    )

    spinner_fmin.js_link('value', fig.x_range, 'start')
    spinner_fmax.js_link('value', fig.x_range, 'end')
    fig.x_range.js_link('start', spinner_fmin, 'value')
    fig.x_range.js_link('end', spinner_fmax, 'value')

    # Add spinner for detailed adjustment of vertical range
    valsformat = bm.formatters.PrintfTickFormatter(format='%.3e')
    spinner_ymin = bm.Spinner(
        title="Plot min vertical",
        format=valsformat
    )

    spinner_ymax = bm.Spinner(
        title="Plot max vertical",
        format=valsformat
    )

    spinner_ymin.js_link('value', fig.y_range, 'start')
    spinner_ymax.js_link('value', fig.y_range, 'end')
    fig.y_range.js_link('start', spinner_ymin, 'value')
    fig.y_range.js_link('end', spinner_ymax, 'value')

    # Add spinner and span for vertical line reference
    ref = bm.Span(
        location=0,
        dimension='height',
        line_color='deeppink',
        line_width=2.0
    )

    spinner_ref = bm.Spinner(
        title="Visual reference frequency",
        format="0.00000",
        value=0,
    )

    fig.add_layout(ref)

    spinner_ref.js_link('value', ref, 'location')
    ref.js_link('location', spinner_ref, 'value')

    # package up all the spinners
    spinners = [
        spinner_fmin,
        spinner_fmax,
        spinner_ref,
        spinner_ymin,
        spinner_ymax,
    ]

    # Update plot title if one was supplied
    if isinstance(title, str):
        fig.title.text = title

    # Spectrum plotted as a line
    spectline = fig.line(
        'freq', 'val',
        source=spectsource,
        color='black')

    # Tooltips for the spectrum itself
    specttips = [
        ("Frequency", "@freq{0.00000}"),
    ]

    # Force the unselected line styling to match the selected line
    spectline.nonselection_glyph = spectline.selection_glyph

    # Add a hover tool for the spectrum
    spect_hover = bm.HoverTool(tooltips=specttips, renderers=[spectline])
    fig.add_tools(spect_hover)

    return fig, spectsource, spinners


def overlay(fig, spectsource, xinds, names, lfreq, colors, markers, sizes,
            tags, legend=None):
    ''' Create a basic spectrum plot.

    Parameters
    ----------
    fig: bokeh figure
        The fig on which to add the overlay
    spectsource: bokeh column data source
        contains: freq, val in a data source
    xinds: 1d numpy array (dtype: int)
        Frequency bin indices where overlay points are located
    names: 1d numpy array (dtype: str)
        Labels from the line list for each overlay point
    lfreq: 1d numpy array (dtype: float)
        Listed frequencies in the line list for each overlay point
    colors: list of strings
        Color for each overlay point
    markers: list of strings
        Marker type for each overlay point (square, circle, triangle..)
    sizes: list of ints
        Marker size for each overlay point
    legend: bool
        Whether or not to add a legend
    tags: list of strings
        Category names for each point (corresponds to color/marker-coding
        and legend)

    Returns
    -------
        fig: bokeh figure
            The now-annotated figure
    '''

    if legend is None:
        if len(set(colors)) == 1:
            legend = False
        else:
            legend = True

    # Alpha currently set to 0.7 for all points; leaving
    # this array here in case we want to amend it
    alphas = np.ones(len(names))*.7

    # Create data source and tooltips
    overlaySource = bp.ColumnDataSource(data={
        'x': spectsource.data['freq'][xinds],
        'y': spectsource.data['val'][xinds],
        'name': names,
        'lfreq': lfreq,
        'color': colors,
        'alpha': alphas,
        'marker': markers,
        'size': sizes,
        'tag': tags,
    })

    overlaytips = [
        ("Description", "@name"),
        ("Frequency bin", "@x{0.00000}"),
        ("Frequency in list", "@lfreq{0.00000}"),
    ]

    # Set up kwargs for the overlay glyphs
    # (Not passing them directly because we want to
    # conditionally pass the legend argument)
    scatter_kwargs = {
        'x': 'x',
        'y': 'y',
        'source': overlaySource,
        'fill_color': 'color',
        'line_color': 'black',
        'fill_alpha': 'alpha',
        'marker': 'marker',
        'size': 'size',
    }

    if legend:
        # Add the legend group
        scatter_kwargs['legend_group'] = 'tag'
        # Note: this line has to be before the overlay scatter,
        # otherwise the legend will be inside the plot area.
        fig.add_layout(bm.Legend(), 'right')
    # Create the actual glyphs
    overlaydots = fig.scatter(**scatter_kwargs)

    # Add a hover tool for the overlay
    overlay_hover = bm.HoverTool(tooltips=overlaytips, renderers=[overlaydots])
    fig.add_tools(overlay_hover)

    return fig


def make_clickable(fig, spectsource):
    '''
    This function adds the ability to click on a spectrum point to annotate it.
    The annotated point is marked with a red dot, and the relevant data is
    logged in a data table.
    '''

    # Create a new copy of the data source to work around a bug.
    ''' Odd as it may seem, there is a bokeh bug which causes segments of the
    line glyph to go invisible when a circle glyph sharing the same source is
    selected. (Confirmed elsewhere.) Creating an independent copy fixes the
    bug.
    '''
    spectsource = bp.ColumnDataSource(spectsource.data.copy())

    # Create invisible dots at each data point on the spectrum.
    '''These dots are a kludgey way to make sure that there is a
    clickable glyph at each point, on which the TapTool can trigger.
    They are mostly just confusing if made visible, although I might
    try showing them on hover later.'''

    spectdots = fig.circle(
        'freq', 'val',
        size=15,
        fill_alpha=0,
        line_alpha=0,
        source=spectsource)

    # Force the unselected dots to have the same styling as the selected ones.
    ''' Prevents a bunch of dots from suddenly becoming visible
    when one is selected.'''

    spectdots.nonselection_glyph = bm.Circle(
        fill_alpha=0,
        line_alpha=0
    )

    # Empty data source for the drawn points.
    drawnsource = bp.ColumnDataSource({
        'x': [],
        'y': [],
        'label': [],
    })

    # Set up glyph styling for drawn points
    drawndots_color = 'red'
    drawndots_selected_linecolor = 'black'
    drawndots_selected_linewidth = 2
    drawndots_nonselected_linecolor = None

    # Renderer for the drawn points.
    drawndots = fig.circle(
        x='x',
        y='y',
        size=10,
        fill_color=drawndots_color,
        line_color=drawndots_nonselected_linecolor,
        source=drawnsource
    )

    # Edit selection glyphs for the drawn points

    drawndots.selection_glyph = bm.Circle(
        fill_alpha=1,
        fill_color=drawndots_color,
        line_color=drawndots_selected_linecolor,
        line_width=drawndots_selected_linewidth
    )

    drawndots.nonselection_glyph = bm.Circle(
        fill_alpha=1,
        fill_color=drawndots_color,
        line_color=drawndots_nonselected_linecolor
    )

    # Create a template for the data table values (num. decimal places)
    template = """
    <%= (value).toFixed(5) %>
    """
    fmat = bm.HTMLTemplateFormatter(template=template)

    # Columns for the data table of drawn points.
    drawncolumns = [
        bm.TableColumn(field='x',
                       title="Frequency",
                       formatter=fmat,
                       editor=bm.widgets.tables.NumberEditor()),
        bm.TableColumn(field='label',
                       title="Label",
                       editor=bm.widgets.tables.StringEditor())
    ]

    # Data table for the drawn points.
    drawntable = bm.DataTable(
        source=drawnsource,
        columns=drawncolumns,
        editable=True,
        height=30)

    # Div to contain the drawn points in CSV format
    div = bm.Div(text="", visible=False)

    # Custom JS code to update the list of drawn points.
    markClick = """
    const pts = drawnsource.data
    var index = spectsource.selected.indices[0]
    var indexindrawn = pts['x'].indexOf(spectsource.data.freq[index])
    if (indexindrawn == -1){
        pts['x'].push(spectsource.data.freq[index])
        pts['y'].push(spectsource.data.val[index])
        pts['label'].push("")
        }
    else {
        pts['x'].splice(indexindrawn,1)
        pts['y'].splice(indexindrawn,1)
        pts['label'].splice(indexindrawn,1)
        }
    drawnsource.data = pts
    drawnsource.change.emit()
    drawntable.height = 30+drawntable.row_height*drawnsource.data.x.length
    """

    csvUpdate = """
    var i
    var text = ""
    for (i=0; i<drawnsource.data.x.length; i++) {
        text+=drawnsource.data.x[i].toFixed(5)+","
        text+=drawnsource.data.label[i]+"<br>"
        }
    div.text = text

    """

    # Callback to update the list of drawn points
    callbackMarkClick = bm.CustomJS(args={
        'spectsource': spectsource,
        'drawnsource': drawndots.data_source,
        'drawntable': drawntable,
        'div': div}, code=markClick+csvUpdate)

    # Tap tool which triggers the custom JS callback when an invisible circle
    # is clicked.
    tap_tool = bm.TapTool(renderers=[spectdots], callback=callbackMarkClick)
    fig.add_tools(tap_tool)
    fig.toolbar.active_tap = tap_tool

    # Button to show/hide spectral data in CSV format
    csvbut = bm.Button(label="Show/hide CSV data table", button_type="default")

    # Custom JS for CSV show/hide
    showCSV = """
    if (div.visible == false) {
        div.visible = true
        }
    else {
        div.visible = false}
    """

    # Callback for CSV show/hide
    callbackShowCSV = bm.CustomJS(args={
        'drawnsource': drawnsource,
        'div': div}, code=csvUpdate+showCSV)

    # Add the callback to the button for CSV show/hide
    csvbut.js_on_event(be.ButtonClick, callbackShowCSV)

    # Return the modified figure and the data table of drawn points
    return fig, drawntable, csvbut, div


def linenames_to_visualtags(names, tagtype='autocolor', groupmin=2):
    '''
    Parameters
    ----------
    names: list of str
        Labels or names of lines from a lines file
    tagtype: str
        one of `tagtypes` given below. Sets the mode for color-coding points.

    Returns
    -------
    colors: list of strings
        Color for each overlay point
    markers: list of strings
        Marker type for each overlay point (square, circle, triangle..)
    sizes: list of ints
        Marker size for each overlay point
    legend: bool
        Whether or not to add a legend
    tags: list of strings
        Category names for each point (corresponds to color/marker-coding
            and legend)
    '''

    # Check against valid color-coding modes
    tagtypes = ['autocolor', 'highlight', 'none']
    if tagtype not in tagtype:
        raise ValueError(f"Invalid tagtype. Expected one of: {tagtypes}")

    # Set up color options
    color_range = [
        "#009bffff",
        "#fff800ff",
        "#ff57d9ff",
        "#9fff48ff",
        "#ff5b5dff",
        "#baa2fbff",
        "#00e8ffff",
        "#8ac14bff",
        "#ffc96aff",
        "#ff8e8fff",
        "#bd43d9ff",
        "#3eaa21ff",
        "#e09b24ff",
        "#9ec7ffff",
        "#9524ffff",
        "#ff96e7ff",
        "#00ffb5ff",
        "#b86958ff",
        "#facbefff",
        "#0cbfa1ff",
        "#2f54fdff",
        "#9d79ffff"
    ]

    # set up marker options
    # note to future: do NOT use inverted_triangle;
    # it causes a silent error
    marker_range = [
        "square",
        "triangle",
        "diamond",
        "plus",
        "star",
        "circle_cross",
        "square_x",
        "triangle_dot",
        "diamond_cross",
        "star_dot",
        "circle_x",
        "square_pin",
        "triangle_pin",
        "diamond_dot",
        "circle_dot",
        "hex",
        "circle_y",
        "square_cross",
        "hex_dot",
        "square_dot",
        "asterisk",
        "x"
    ]

    colorcycle = itertools.cycle(color_range)
    markercycle = itertools.cycle(marker_range)
    tagdefault = "all other entries"

    # We need to turn the names into a set of "tags" that will define
    # groups of lines for color-coding.

    if tagtype == "autocolor":
        # If we are auto-coloring, ignore parenthetical notes
        # and strip off whitespace
        notechar = "("
        tags = []
        for n in names:
            if notechar in n:
                tag, othernote = n.split(notechar, 1)
                tag = tag.strip()
            else:
                tag = n.strip()
            tags += [tag]

    elif tagtype == "highlight":
        # If we are in highlight mode, pay attention to things
        # after the exclamation point.
        # Also strip off whitespace.
        tagchar = "!"
        tags = []
        for n in names:
            if tagchar in n:
                othernote, tag = n.split(tagchar)
                tag = tag.strip()
            else:
                # Group everything without a ! into the default category
                tag = tagdefault
            tags += [tag]
    else:
        # If we aren't in a highlight or autocolor mode, everything
        # gets the default tag
        tags = [tagdefault]*len(names)
    # Compute the unique tags and their counts.
    # Order by counts in descending order.
    tags = np.array(tags)
    utags, taginds, counts = np.unique(
        tags, return_inverse=True, return_counts=True)
    tagorder = np.argsort(counts)[::-1]
    # If a group min size was set, reset everything under that group
    # size to the default tag
    if len(tags) > 0 and groupmin > 1:
        tags[counts[taginds] < groupmin] = tagdefault
    utags, counts = np.unique(tags, return_counts=True)
    tagorder = np.argsort(counts)[::-1]

    # Create the colors and markers arrays, which are currently empty
    colors = np.array([""]*len(names), dtype='<U16')
    markers = np.array([""]*len(names), dtype='<U16')
    sizes = np.ones(len(names))*11

    # Loop through the unique tags and set all corresponding color
    # array entries to the corresponding color.
    for utag in utags[tagorder]:
        if utag == "all other entries":
            color = "lightgray"
            marker = "circle"
        else:
            color = next(colorcycle)
            marker = next(markercycle)
        tagplaces = np.where(tags == utag)[0]
        for pattern in ["triangle", "diamond", "star", "hex"]:
            if pattern in marker:
                sizes[tagplaces] = 16
        colors[tagplaces] = color
        markers[tagplaces] = marker

    return colors, markers, sizes, tags


def main(args=None):

    if args is None:
        args = get_args()

    # Load spectral data and clip to user-specified bounds
    freq, val = io.load_spect_from_fscan_npz(
        args.spectfile,
        freqname=args.freqcolname,
        dataname=args.datacolname)
    freq, val = slt.clip_spect(freq, val, args.fmin, args.fmax)

    # Load lines data, if any, and clip to bounds matching spectrum
    linds, lnames, lfreq = [], [], []
    if args.linesfile:
        lfreq, lnames = io.load_lines_from_linesfile(args.linesfile)
        if len(lfreq) > 0:
            lfreq, lnames = slt.clip_spect(
                lfreq, lnames, freq[0], freq[-1], islinefile=True)
            linds = slt.match_bins(freq, lfreq)

    # If the user didn't specify color coding, try to guess based on
    # the contents of the lines file. Default to auto-coloring.
    if not args.colorcode:
        args.colorcode = 'autocolor'
        if args.linesfile:
            if "!" in "".join(lnames):
                args.colorcode = 'highlight'

    # Get ready to load comb data, if any, by setting up arrays
    combinds = np.zeros(0)  # spectral indices of teeth
    combnames = np.zeros(0)  # labels of teeth
    combfreq = np.zeros(0)  # frequencies of teeth

    if args.plotcombs:
        # loop over specified combs
        for combarg in args.plotcombs:
            sp, off = io.combarg_to_combparams(combarg)
            jcombfreq, jcombinds, jcombnames = slt.combparams_to_labeled_teeth(
                sp, off, freq, np.arange(0, len(freq), 1))

            # Append to the waiting arrays
            combinds = np.append(combinds, jcombinds)
            combnames = np.append(combnames, jcombnames)
            combfreq = np.append(combfreq, jcombfreq)

    # Concatenate the line and comb data
    inds = np.append(linds, combinds).astype(int)
    names = np.append(lnames, combnames)
    tagfreq = np.append(lfreq, combfreq)

    # If asked to intersect with linefinder results
    if args.intersect_linefinder:
        # convert the running median window to bins
        medwindow_bins = int(args.peakmedwindow /
                             (freq[-1] - freq[0]) * len(freq))
        # get indices of peaks that pass the cuts
        peaks = linefinder.peaks(val, args.peaksensitivity, medwindow_bins)
        # filter line data based on whether it's in the peak data
        filt = np.isin(inds, peaks)
        inds = inds[filt]
        names = names[filt]
        tagfreq = tagfreq[filt]

    # Convert the lines to visual tags (markers, colors, etc for glyphs)
    colors, markers, sizes, tags = linenames_to_visualtags(
        names,
        tagtype=args.colorcode,
        groupmin=args.colorcode_group_min)

    # Plot the spectrum
    fig, spectsource, spinners = plot_spect(
        outfile=args.outfile,
        freq=freq,
        val=val,
        title=args.title,
        yaxlabel=args.yaxlabel,
        ylog=args.ylog
    )

    # Overlay the line and comb data
    fig = overlay(fig,
                  spectsource,
                  inds,
                  names,
                  tagfreq,
                  colors,
                  markers,
                  sizes,
                  tags,
                  legend=args.legend
                  )

    # If the user requested an annotatable plot
    # add the clickable features and save
    if args.annotate:
        fig, drawntable, csvbut, div = make_clickable(fig, spectsource)
        bp.save(bl.column(
            fig,
            bl.row(spinners),
            drawntable,
            csvbut,
            div,
            sizing_mode='stretch_width'
        ))

    # Otherwise, just save as-is
    else:
        bp.save(bl.column(
            fig,
            bl.row(spinners),
            sizing_mode='stretch_width'
        ))
