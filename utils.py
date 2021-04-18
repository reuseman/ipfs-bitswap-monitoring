import pandas as pd

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
#     # Print New Line on Complete
#     if iteration == total: 
#         print()

def show_peers_table(partners):
    import plotly.graph_objects as go
    import humanfriendly

    peers_table = []
    
    for col in ["Peer", "Recv", "Exchanged", "Country", "Latency"]:
        current_column = []
        for cid in partners.keys():
            info = partners[cid]
            if col == "Recv":
                current_column.append(humanfriendly.format_size(info[col]))
            else:
                current_column.append(info[col])
        peers_table.append(current_column)

    if len(partners) > 0:
        fig = go.Figure(data=[go.Table(
            header=dict(values=['Peer', 'Received data', 'Blocks', 'Country', 'Latency'],
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=peers_table,
                       line_color='darkslategray',
                       fill_color='lightcyan',
                       align='left'))
        ])

        fig.update_layout(width=800, height=400)
        fig.show()
    else:
        print("- No peers at the moment")


def partners_to_df(partners, df_old=pd.DataFrame()):
    from datetime import datetime
        
    data = dict()
    for col in next(iter(partners.values())).keys():
        data[col] = []
        for cid in partners.keys():
            value = partners[cid][col]
            # Removes "ms"
            if col == "Latency":
                value = value[:-2]
            data[col].append(value)

    df = pd.DataFrame(data)
    df.insert(0, 'Timestamp', datetime.now().isoformat())
    
    if not df_old.empty:
        df = df_old.append(df)
    
    return df
