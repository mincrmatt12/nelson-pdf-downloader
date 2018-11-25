import niter
import downloader
import tree
import click
import io
import tempfile
import os
import subprocess

@click.command()
@click.option('-p', '--product', type=int, prompt="Product ID (find url of explorer pid)", help="Nelson Product ID")
@click.option("--session", type=str, prompt="Session ID (find by logging in and copying it)", help="JSESSIONID")
@click.option("--server", type=str, prompt="Server ID (weird tomcat server id)")
@click.option("-o", "--output", type=click.Path(writable=True), default="output.pdf")
def main(product, session, server, output):
    book = niter.Book(product, session, server)
    click.echo("Using book {}".format(book.title))

    urls, names = tree.get_tree_url(book)
    all_contents = downloader.download_all(urls, book)
    click.echo("Got {} PDFs to merge".format(len(all_contents)))

    with tempfile.TemporaryDirectory() as tempdir:
        files = []
        for i, f in enumerate(all_contents):
            with open(os.path.join(tempdir, "{}.pdf".format(i)), "wb") as g:
                g.write(f)
            files.append(os.path.join(tempdir, "{}.pdf".format(i)))
        
        args = ["qpdf", "--empty", "--pages"]
        for i in files:
            args.append(i)
            args.append("1-z")
        args.extend(["--", output])
        subprocess.run(args, check=True)

    click.echo("Done!")

if __name__ == "__main__":
    main()
