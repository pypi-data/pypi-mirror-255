

def chart_for_mazai(fig, name, path='.'):
    """Save the figure as html file, and display it"""

    # Save the html file
    path += '/charts/' + str(name) + '.html'
    fig.write_html(path, full_html=False, include_plotlyjs=False)

    # Display the keyword, and the file
    print(f'#! FIGURE {str(name)} #!')
    fig.show()
