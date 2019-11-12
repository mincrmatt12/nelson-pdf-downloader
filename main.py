import niter
import downloader
import merger
import tree
import click
import io
import tempfile
import os
import subprocess

@click.command()
@click.option('-p', '--product', type=int, prompt="Product ID (find url of explorer pid)", help="Nelson Product ID")
@click.option("--session", type=str, prompt="Session ID (find by logging in and copying it)", help="Cookie: JSESSIONID")
@click.option("--server", type=str, prompt="Server ID (weird tomcat server id)")
@click.option("-o", "--output", type=click.Path(writable=True), default="output.pdf")
@click.option("--tree-index", type=int, default=1, help="Which tree index (in navigation view, first column, which entry has the PDFs) to download from (default 1, 0-indexed)")
@click.option("--first-page", type=int, default=2, help="What numerical page does the book start at in the PDFs")
def main(product, session, server, output, tree_index, first_page):
    book = niter.Book(product, session, server)
    click.echo("Using book {}".format(book.title))

    urls, names = tree.get_tree_url(book, tree_index)
    all_contents = downloader.download_all(urls, book)
    click.echo("Got {} PDFs to merge".format(len(all_contents)))
    merged_contents = merger.merge(all_contents, names, output, first_page)

    click.echo("Done!")

if __name__ == "__main__":
    main()
