import niter 
import click
import colorama
from tqdm import tqdm

def recurse(level: niter.Level):
    x = [level]
    if len(level) != 0:
        for i in tqdm(level, leave=False, desc="Looking up {}".format(level.title)):
            x.extend(recurse(i))
    return x

def get_tree_url(book_obj: niter.Book):
    """
    Grab the list of pdfs from a Book object.

    This makes some assumptions about the internal structure of the links in the book, so it quickly confirms
    with the user if the name makes sense.
    """

    if len(book_obj) != 2:
        click.echo(colorama.Fore.RED + "Invalid book structure, manually change script to download.", err=True)
        raise click.Abort()

    if not click.confirm("Book tree name is {}, does this make sense? ".format(book_obj[1].title)):
        raise click.Abort()
    
    child_attrs = recurse(book_obj[1])
    urls = []
    names = []

    for i in tqdm(child_attrs, desc="Looking up URLs"):
        if i.has_links:
            for b in i.link_info:
                if b.file_type == "PDF":
                    urls.append(b.url)
                    names.append(b.title.replace("Student Book PDF", ""))

    return urls, names
