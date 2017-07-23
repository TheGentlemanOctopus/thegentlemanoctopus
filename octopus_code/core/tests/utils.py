import matplotlib.pyplot as plt

def new_axes():
    fig = plt.figure()
    ax = plt.axes()
    fig.add_axes(ax)
    return ax