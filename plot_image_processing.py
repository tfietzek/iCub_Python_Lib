"""
Created on Thu Apr 13 15:16:32 2018

@author: Torsten Fietzek

library for image processing functions
"""

import math

import cv2
import matplotlib.pylab as plt
import numpy as np


####################################################
# show image with matplotlib, with x- and y-label
def show_image_matplot(plot_image, title, xlabel, ylabel):
    """
    Plot image with matplotlib and the given parameters and colormap gray.

    Parameters
    ----------
    plot_image : NDarray
        Image to plot.
    title : str
        Title of the image.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for they-axis
    """
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.imshow(plot_image, cmap='gray', interpolation=None)
    plt.colorbar()

    plt.show()
    plt.pause(0.05)


####################################################
# show image with matplotlib, define axis ranges and axis labels
def show_matplot_all_label(plot_image, title, xlabel, ylabel, xtick=[None, None], ytick=[None, None]):
    """
    Plot image with matplotlib and the given parameters and colormap gray.

    Parameters
    ----------
    plot_image : NDarray
        Image to plot.
    title : str
        Title of the image.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for they-axis
    xtick : list, optional
        ticks and tick labels for the x-axis, if set to None default ticks/labels will be used, by default [None, None]
    ytick : list, optional
        ticks and tick labels for the y-axis, if set to None default ticks/labels will be used, by default [None, None]
    """
    plt.figure(figsize=(7, 5.5))

    plt.title(title, fontsize=16, y=1.02)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)

    plt.imshow(plot_image, cmap='gray', interpolation=None)
    plt.colorbar().ax.tick_params(labelsize=13)

    # set axis tick ranges and labels
    plt.xticks(xtick[0], xtick[1], fontsize=13)
    plt.yticks(ytick[0], ytick[1], fontsize=13)

    plt.show()
    plt.pause(0.05)


####################################################
# show image with matplotlib
# define range and axis labels
def show_matplot_all_label_clr(plot_image, title, xlabel, ylabel, xtick=[None, None], ytick=[None, None], clr_map='gray', size=(7, 5.5)):
    """
    Plot image with matplotlib and the given parameters.

    Parameters
    ----------
    plot_image : NDarray
        Image to plot.
    title : str
        Title of the image.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for they-axis
    xtick : list, optional
        ticks and tick labels for the x-axis, if set to None default ticks/labels will be used, by default [None, None]
    ytick : list, optional
        ticks and tick labels for the y-axis, if set to None default ticks/labels will be used, by default [None, None]
    clr_map : str
        Colormap descriptor for matplotlib
    size : tuple, optional
        Size of the generated figure, by default (7, 5.5)
    """
    plt.figure(figsize=size)

    plt.title(title, fontsize=16, y=1.02)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)

    plt.imshow(plot_image, cmap=clr_map, interpolation=None)
    plt.colorbar().ax.tick_params(labelsize=13)

    # set axis tick ranges and labels
    plt.xticks(xtick[0], xtick[1], fontsize=13)
    plt.yticks(ytick[0], ytick[1], fontsize=13)

    plt.show()
    plt.pause(0.05)


####################################################
# show signal with opencv
def show_signal_opencv(signal, title, step):
    '''
    show a given 2D-signal sequence as a sequence of images

    params: signal      -- array containing the input for all timesteps
            title       -- name of the signal
            step        -- stepsize of the shown signal
    '''

    # preprocess signal to get a list with valid signal images
    sig = []
    j = 0
    for i in range(0, signal.shape[0]):
        if j % step == 0:  # change stepsize from 1ms to the given stepsize
            # -1 if not used the timestep (dummy signal longer then simulated signal)
            if signal[i][0][0] != -1:
                sig.append(signal[i].T)
            else:
                break
        j += 1

    # show this generated list of valid signal images
    cv2.namedWindow(title)
    cv2.waitKey()
    j = 0
    for i in sig:
        # normalize to interval [0, 255]
        maxim = np.amax(i)
        if maxim > 0:
            i = i / maxim * 255
        # resize to larger image for better view
        img = cv2.resize(i, (420, 300), interpolation=cv2.INTER_NEAREST)
        # show image
        print('img:', j)
        cv2.imshow('sig', img)
        cv2.waitKey(40)
        j += step
    cv2.waitKey()
    cv2.destroyAllWindows()


####################################################
# show signal
def show_signal(signals, disp, sig_key, opt, timestep, step):
    '''
    execute the selected options for the selected signal

    params: signals     -- dictonary containing the signals of all simulated displacements
            disp        -- selected displacement
            sig_key     -- selected key of the signal to be shown
            opt         -- dictionary of selected options
            timestep    -- selected timestep to be shown
            step        -- stepsize of the shown signal
    '''

    # set signal with given displacement
    signal = signals[disp]

    # set signal with given key
    signal_1 = signal[sig_key]

    # execute chosen options
    # show whole signal
    if 'opencv' in opt:
        show_signal_opencv(signal_1, sig_key, step)
    # show specific timestep
    if 'matplotlib' in opt:
        show_image_matplot(signal_1[timestep], sig_key,
                           'x view angle', 'y view angle')
    # save signal 'sig_key' at timestep 'timestep' in a file
    if 'save' in opt:
        np.save(sig_key + '_img', signal_1[timestep])


####################################################
# show 4D array with matplotlib
def show_4Darray_matplot(plot_image, title, h_plot, v_plot, save=False, save_dir="", save_type=".svg"):
    """
    Plot a 4D numpy array

    Parameters
    ----------
    plot_image : NDarray
        4D array to plot
    title : str
        title of the plot
    h_plot : int
        number of images in horizontal direction
    v_plot : int
        number of images in vertical direction
    save : bool, optional
        save plot to file, by default False
    save_dir : str, optional
        save path, by default ""
    save_type : str, optional
        file type for plot file, by default ".svg"
    """
    plot_img_count = h_plot * v_plot
    h_step = 0
    v_step = 0
    img_count = plot_image.shape[2] * plot_image.shape[3]

    for i in range(math.ceil(img_count / plot_img_count)):
        plt.figure(figsize=(13, 10))
        plt.tight_layout()
        for j in range(plot_img_count):
            if (j + i * plot_img_count) < img_count:
                plt.subplot(v_plot, h_plot, j + 1)
                plt.imshow(plot_image[:, :, h_step, v_step].T, cmap='gray')
                plt.colorbar()
                plt.xticks([])
                plt.yticks([])
            else:
                break
            v_step += 1
            if v_step == plot_image.shape[3]:
                v_step = 0
                h_step += 1
        plt.suptitle(title)
        plt.tight_layout(pad=2.5, w_pad=0.5, h_pad=1.0)
        if save:
            plt.savefig(save_dir + title.replace(" ", "_") + save_type)
            plt.close()
        else:
            plt.show()
            plt.pause(0.05)
