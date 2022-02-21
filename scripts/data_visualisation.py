import csv
import matplotlib.pyplot as plt


def load_csv(filename):
    # A list of dictionaries to hold each dataset.
    data = [
        {'Title': 'AWS Sharpness',
         'Column Index': 2,
         'Reverse Axis': False,
         'Data': []},
        {'Title': 'Laplacian Variance',
         'Column Index': 5,
         'Reverse Axis': False,
         'Data': []},
        {'Title': 'Perceptual Blur Metric',
         'Column Index': 9,
         'Reverse Axis': True,
         'Data': []},
        {'Title': 'Tenengrad Variance',
         'Column Index': 13,
         'Reverse Axis': False,
         'Data': []},
        {'Title': 'Wavelet Coefficients Variance',
         'Column Index': 17,
         'Reverse Axis': False,
         'Data': []}
        ]

    # Add a sub-list for each blur image in the 'Data' list.
    n_blurs = 6
    for d in data:
        for n in range(n_blurs):
            d['Data'].append([])

    # Open the csv and parse each line, assigning the values to the Data key
    # of each dataset dictionary.
    with open(filename, 'r', newline='\n') as csvfile:
        results = csv.reader(csvfile, delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_NONNUMERIC)
        headers = next(results)

        # The values from each row are copied into the appropriate list and
        # sub-list.
        for i, row in enumerate(results):
            for d in data:
                d['Data'][i % n_blurs].append(row[d['Column Index']])
            
    return data

def create_histograms(input_data, save_name):
    # Create a stack of plots, appropriately sized for display on an A4 PDF,
    # two per page.
    fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(8.2677, 29.23),
                            dpi=300.0)
    n_bins = 50
    colours = ['blanchedalmond', 'gold', 'orange',
               'tomato', 'firebrick', 'maroon']
    
    for ax, data in zip(axs, input_data):
        ax.hist(data['Data'], n_bins, histtype='bar', stacked=True,
                color=colours)
        ax.legend([0, 1, 2, 3, 4, 5], loc='upper right', title='Blur amount')
        ax.set_title(data['Title'], pad=12)
        if data['Reverse Axis'] == True:
            ax.invert_xaxis()
        ax.set_xlabel('Sharpness Value', labelpad=10)
        ax.set_ylabel('Frequency', labelpad=12)

    # Adjust border spacing and save.
    fig.subplots_adjust(left=0.13, right=0.92,
                        bottom=0.03, top=0.97,
                        hspace=0.28, wspace=0.1)
    plt.savefig(save_name)

def create_boxplots(input_data, save_name):
    # Create a stack of plots, appropriately sized for display on an A4 PDF,
    # one per page.
    fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(8.2677, 58.46),
                            dpi=300.0)

    for ax, data in zip(axs, input_data):
        ax.boxplot(data['Data'],
                   vert=True,
                   medianprops=dict(color='red'),
                   whis=(2, 98),
                   showfliers=False,
                   labels=[0, 1, 2, 3, 4, 5])
        ax.set_title(data['Title'], pad=18)
        if data['Reverse Axis'] == True:
            ax.invert_yaxis()
        ax.set_xlabel('Gaussian Blur Amount (\u03C3)', labelpad=12)
        ax.set_ylabel('Sharpness Value', labelpad=12)

    # Adjust border spacing and save.
    fig.subplots_adjust(left=0.15, right=0.90,
                        bottom=0.025, top=0.98,
                        hspace=0.24, wspace=0.1)
    plt.savefig(save_name)

if __name__ == '__main__':
    data = load_csv('results.csv')
    create_histograms(data, 'histograms.png')
    create_boxplots(data, 'boxplots.png')
