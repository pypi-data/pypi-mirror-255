import click
import pyperclip
from tabulate import tabulate

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@click.command()
@click.option('-f', '--fmt', default='ascii', help='Output format: ascii or csv. Default is ascii.')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output.')
@click.option('--ascii-style', default='presto', help='Style of the ascii table. Default is presto.')
def main(fmt, verbose, ascii_style):
    raw_data = pyperclip.paste()
    raw_data = raw_data.replace("\r", "").split("\n")
    header = raw_data[0].split()
    columns = raw_data[1:]

    n_cols = len(header)

    csv_output = "; ".join(header) + "\n"
    col_data = []
    for row in chunks(columns, n_cols):
        col_data.append(row)
        csv_output += "; ".join(row)
        csv_output += "\n"

    if fmt == "ascii":
        ascii_output = tabulate(col_data, header, tablefmt=ascii_style)
        pyperclip.copy(ascii_output)
        if verbose:
            click.echo(ascii_output)
    elif fmt == "csv":
        pyperclip.copy(csv_output)
        if verbose:
            click.echo(csv_output)
    return
 
 
 