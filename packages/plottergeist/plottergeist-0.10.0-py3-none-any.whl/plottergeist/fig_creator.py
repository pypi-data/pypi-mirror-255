import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def make_plot(ndim: int, pull: bool = False, figsize=None):
    if ndim not in [1, 2, 3, 5, 6]:
        raise ValueError(
            "ERROR: currently supported values for ndim are 1, 2, 3, 5 and 6.\
                          Please consider creating your own figure from plottergeist functions."
        )
    if ndim == 1:
        if pull:
            return make_plot_1D_with_pull(figsize)
        return make_plot_1D_without_pull(figsize)
    elif ndim == 2:
        if pull:
            return make_plot_2D_with_pull(figsize)
        return make_plot_2D_without_pull(figsize)
    elif ndim == 3:
        if pull:
            return make_plot_3D_with_pull(figsize)
        return make_plot_3D_without_pull(figsize)
    elif ndim == 5:
        if pull:
            return make_plot_5D_with_pull(figsize)
        return make_plot_5D_without_pull(figsize)
    if pull:
        return make_plot_6D_with_pull(figsize)
    return make_plot_6D_without_pull(figsize)


def make_plot_2D_without_pull(figsize):
    fig = plt.figure(figsize=figsize)

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    for axplot in axes:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    return fig, axes


def make_plot_2D_with_pull(figsize):
    fig = plt.figure(figsize=figsize)

    fig, axes = plt.subplots(
        2,
        2,
        figsize=figsize,
        sharex=True,
        gridspec_kw={"height_ratios": [10, 3], "hspace": 0.01},
    )

    ax1, ax2, ax1pull, ax2pull = axes.flatten()

    for axplot in [ax1, ax2]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    for axpull in [ax1pull, ax2pull]:
        axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
        axpull.set_ylim(-7, 7)
        axpull.set_yticks([-5, -3, 0, +3, +5])
        # axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
        axpull.set_yticklabels([-5, -3, 0, 3, 5])
        axpull.tick_params(
            which="major",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axpull.tick_params(
            which="minor",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        # axpull.set_ylabel("Pull", fontsize=14)
        axpull.set_ylabel("Pull")

    return fig, (ax1, ax2), (ax1pull, ax2pull)


def make_plot_1D_with_pull(figsize):
    fig = plt.figure(figsize=figsize)

    outer = gridspec.GridSpec(1, 1, figure=fig)

    gs1 = gridspec.GridSpecFromSubplotSpec(
        2, 1, subplot_spec=outer[0], height_ratios=[10, 3], hspace=0.01
    )

    ax = fig.add_subplot(gs1[0])
    axpull = fig.add_subplot(gs1[1], sharex=ax)

    ax.yaxis.set_major_locator(plt.MaxNLocator(8))
    ax.tick_params(
        which="major",
        length=8,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    ax.tick_params(
        which="minor",
        length=6,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )

    axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
    axpull.set_ylim(-7, 7)
    axpull.set_yticks([-5, -3, 0, +3, +5])
    # axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
    axpull.set_yticklabels([-5, -3, 0, 3, 5])
    axpull.tick_params(
        which="major",
        length=4,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    axpull.tick_params(
        which="minor",
        length=4,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    # axpull.set_ylabel("Pull", fontsize=14)
    axpull.set_ylabel("Pull")

    fig.align_ylabels()

    return fig, ax, axpull


def make_plot_1D_without_pull(figsize):
    fig = plt.figure(figsize=figsize)

    gs = gridspec.GridSpec(1, 1, figure=fig)

    ax = fig.add_subplot(gs[0])

    ax.yaxis.set_major_locator(plt.MaxNLocator(8))
    ax.tick_params(
        which="major",
        length=8,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    ax.tick_params(
        which="minor",
        length=6,
        width=1,
        direction="in",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )

    return fig, ax


def make_plot_3D_with_pull(figsize):
    fig = plt.figure(figsize=figsize)

    outer = gridspec.GridSpec(2, 1, figure=fig)

    gs1 = gridspec.GridSpecFromSubplotSpec(
        2, 2, subplot_spec=outer[0], height_ratios=[10, 3], hspace=0.01
    )
    gs2 = gridspec.GridSpecFromSubplotSpec(
        2, 2, subplot_spec=outer[1], height_ratios=[10, 3], hspace=0.01
    )

    ax1 = fig.add_subplot(gs1[0])
    ax1pull = fig.add_subplot(gs1[2], sharex=ax1)

    ax2 = fig.add_subplot(gs1[1])
    ax2pull = fig.add_subplot(gs1[3], sharex=ax2)

    # ax3 = fig.add_subplot(gs1[2])
    # ax3pull = fig.add_subplot(gs1[5], sharex=ax3)

    ax3 = fig.add_subplot(gs2[0])
    ax3pull = fig.add_subplot(gs2[2], sharex=ax3)

    ax4 = fig.add_subplot(gs2[1])
    # ax5pull = fig.add_subplot(gs2[4], sharex=ax5)

    # ax6 = fig.add_subplot(gs2[2])

    for axplot in [ax1, ax2, ax3, ax4]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    for axpull in [ax1pull, ax2pull, ax3pull]:
        axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
        axpull.set_ylim(-7, 7)
        axpull.set_yticks([-5, -3, 0, +3, +5])
        # axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
        axpull.set_yticklabels([-5, -3, 0, 3, 5])
        axpull.tick_params(
            which="major",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axpull.tick_params(
            which="minor",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        # axpull.set_ylabel("Pull", fontsize=14)
        axpull.set_ylabel("Pull")

    fig.align_ylabels()

    return fig, (ax1, ax2, ax3), ax4, (ax1pull, ax2pull, ax3pull)


def make_plot_3D_without_pull(figsize):
    fig = plt.figure(figsize=figsize)

    gs1 = gridspec.GridSpec(2, 2, figure=fig)

    # gs1 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec = outer[0], height_ratios = [10, 3], hspace=0.01)
    # gs2 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec = outer[1], height_ratios = [10, 3], hspace=0.01)

    ax1 = fig.add_subplot(gs1[0])
    # ax1pull = fig.add_subplot(gs1[2], sharex=ax1)

    ax2 = fig.add_subplot(gs1[1])
    # ax2pull = fig.add_subplot(gs1[3], sharex=ax2)

    # ax3 = fig.add_subplot(gs1[2])
    # ax3pull = fig.add_subplot(gs1[5], sharex=ax3)

    ax3 = fig.add_subplot(gs1[2])
    # ax3pull = fig.add_subplot(gs2[2], sharex=ax3)

    ax4 = fig.add_subplot(gs1[3])
    # ax5pull = fig.add_subplot(gs2[4], sharex=ax5)

    # ax6 = fig.add_subplot(gs2[2])

    for axplot in [ax1, ax2, ax3, ax4]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    # for axpull in [ax1pull, ax2pull, ax3pull]:
    #   axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
    #   axpull.set_ylim(-7, 7)
    #   axpull.set_yticks([-5, -3, 0, +3, +5])
    #   axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
    #   axpull.tick_params(which='major', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)
    #   axpull.tick_params(which='minor', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)
    #   axpull.set_ylabel("Pull", fontsize=14)
    #
    # fig.align_ylabels()

    return fig, (ax1, ax2, ax3), ax4


def make_plot_5D_with_pull(figsize):
    fig = plt.figure(figsize=figsize)

    outer = gridspec.GridSpec(2, 1, figure=fig)

    gs1 = gridspec.GridSpecFromSubplotSpec(
        2, 3, subplot_spec=outer[0], height_ratios=[10, 3], hspace=0.01
    )
    gs2 = gridspec.GridSpecFromSubplotSpec(
        2, 3, subplot_spec=outer[1], height_ratios=[10, 3], hspace=0.01
    )

    ax1 = fig.add_subplot(gs1[0])
    ax1pull = fig.add_subplot(gs1[3], sharex=ax1)

    ax2 = fig.add_subplot(gs1[1])
    ax2pull = fig.add_subplot(gs1[4], sharex=ax2)

    ax3 = fig.add_subplot(gs1[2])
    ax3pull = fig.add_subplot(gs1[5], sharex=ax3)

    ax4 = fig.add_subplot(gs2[0])
    ax4pull = fig.add_subplot(gs2[3], sharex=ax4)

    ax5 = fig.add_subplot(gs2[1])
    ax5pull = fig.add_subplot(gs2[4], sharex=ax5)

    ax6 = fig.add_subplot(gs2[2])
    # ax6pull = fig.add_subplot(gs2[5], sharex=ax6)

    # for axplot in [ax1, ax2, ax3, ax4, ax5, ax6]:
    for axplot in [ax1, ax2, ax3, ax4, ax5]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    # for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull, ax6pull]:
    for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull]:
        axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
        axpull.set_ylim(-7, 7)
        axpull.set_yticks([-5, -3, 0, +3, +5])
        # axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
        axpull.set_yticklabels([-5, -3, 0, 3, 5])
        axpull.tick_params(
            which="major",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axpull.tick_params(
            which="minor",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        # axpull.set_ylabel("Pull", fontsize=14)
        axpull.set_ylabel("Pull")

    fig.align_ylabels()

    return (
        fig,
        (ax1, ax2, ax3, ax4, ax5),
        ax6,
        (ax1pull, ax2pull, ax3pull, ax4pull, ax5pull),
    )
    # return fig, (ax1, ax2, ax3, ax4, ax5, ax6), (ax1pull, ax2pull, ax3pull, ax4pull, ax5pull, ax6pull)


def make_plot_5D_without_pull(figsize):
    fig = plt.figure(figsize=figsize)

    gs1 = gridspec.GridSpec(2, 3, figure=fig)

    # gs1 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec = outer[0], height_ratios = [10, 3], hspace=0.01)
    # gs2 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec = outer[1], height_ratios = [10, 3], hspace=0.01)

    ax1 = fig.add_subplot(gs1[0])

    ax2 = fig.add_subplot(gs1[1])

    ax3 = fig.add_subplot(gs1[2])

    ax4 = fig.add_subplot(gs1[3])

    ax5 = fig.add_subplot(gs1[4])

    ax6 = fig.add_subplot(gs1[5])

    for axplot in [ax1, ax2, ax3, ax4, ax5]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    # for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull]:
    #   axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
    #   axpull.set_ylim(-7, 7)
    #   axpull.set_yticks([-5, 0, +5])
    #   axpull.tick_params(which='major', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)
    #   axpull.tick_params(which='minor', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)

    return fig, (ax1, ax2, ax3, ax4, ax5), ax6


def make_plot_6D_with_pull(figsize):
    fig = plt.figure(figsize=figsize)

    outer = gridspec.GridSpec(2, 1, figure=fig)

    gs1 = gridspec.GridSpecFromSubplotSpec(
        2, 3, subplot_spec=outer[0], height_ratios=[10, 3], hspace=0.01
    )
    gs2 = gridspec.GridSpecFromSubplotSpec(
        2, 3, subplot_spec=outer[1], height_ratios=[10, 3], hspace=0.01
    )

    ax1 = fig.add_subplot(gs1[0])
    ax1pull = fig.add_subplot(gs1[3], sharex=ax1)

    ax2 = fig.add_subplot(gs1[1])
    ax2pull = fig.add_subplot(gs1[4], sharex=ax2)

    ax3 = fig.add_subplot(gs1[2])
    ax3pull = fig.add_subplot(gs1[5], sharex=ax3)

    ax4 = fig.add_subplot(gs2[0])
    ax4pull = fig.add_subplot(gs2[3], sharex=ax4)

    ax5 = fig.add_subplot(gs2[1])
    ax5pull = fig.add_subplot(gs2[4], sharex=ax5)

    ax6 = fig.add_subplot(gs2[2])
    ax6pull = fig.add_subplot(gs2[5], sharex=ax6)

    for axplot in [ax1, ax2, ax3, ax4, ax5, ax6]:
        # for axplot in [ax1, ax2, ax3, ax4, ax5]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull, ax6pull]:
        # for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull]:
        axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
        axpull.set_ylim(-7, 7)
        axpull.set_yticks([-5, -3, 0, +3, +5])
        # axpull.set_yticklabels([-5, -3, 0, 3, 5], fontdict={"fontsize": 8})
        axpull.set_yticklabels([-5, -3, 0, 3, 5])
        axpull.tick_params(
            which="major",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axpull.tick_params(
            which="minor",
            length=4,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        # axpull.set_ylabel("Pull", fontsize=14)
        axpull.set_ylabel("Pull")

    fig.align_ylabels()

    # return fig, (ax1, ax2, ax3, ax4, ax5), ax6, (ax1pull, ax2pull, ax3pull, ax4pull, ax5pull)
    return (
        fig,
        (ax1, ax2, ax3, ax4, ax5, ax6),
        (ax1pull, ax2pull, ax3pull, ax4pull, ax5pull, ax6pull),
    )


def make_plot_6D_without_pull(figsize):
    fig = plt.figure(figsize=figsize)

    gs1 = gridspec.GridSpec(2, 3, figure=fig)

    # gs1 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec = outer[0], height_ratios = [10, 3], hspace=0.01)
    # gs2 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec = outer[1], height_ratios = [10, 3], hspace=0.01)

    ax1 = fig.add_subplot(gs1[0])

    ax2 = fig.add_subplot(gs1[1])

    ax3 = fig.add_subplot(gs1[2])

    ax4 = fig.add_subplot(gs1[3])

    ax5 = fig.add_subplot(gs1[4])

    ax6 = fig.add_subplot(gs1[5])

    for axplot in [ax1, ax2, ax3, ax4, ax5, ax6]:
        axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
        axplot.tick_params(
            which="major",
            length=8,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )
        axplot.tick_params(
            which="minor",
            length=6,
            width=1,
            direction="in",
            bottom=True,
            top=True,
            left=True,
            right=True,
        )

    # for axpull in [ax1pull, ax2pull, ax3pull, ax4pull, ax5pull]:
    #   axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
    #   axpull.set_ylim(-7, 7)
    #   axpull.set_yticks([-5, 0, +5])
    #   axpull.tick_params(which='major', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)
    #   axpull.tick_params(which='minor', length=4, width=1, direction='in',
    #                     bottom=True, top=True, left=True, right=True)

    return fig, (ax1, ax2, ax3, ax4, ax5), ax6
