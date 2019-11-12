import pikepdf
import io
import tqdm
import click

def get_real_name(name):
    """
    strip the things out of the name to make it more useful
    """

    # add other terms here
    return name.replace(" Student Book PDF", "")

def is_contents(name):
    return "content" in name.lower()

def append_pdf(pdf_out, pdf_in_stream, name):
    """
    add to out in with outline name
    """

    pdf_in = pikepdf.open(io.BytesIO(pdf_in_stream))

    pdf_out.pages.extend(pdf_in.pages)

    if "/Outlines" not in pdf_out.root:
        pdf_out.root.Outlines = pdf_out.make_indirect({
            "/First": pdf_out.make_indirect({
                "/Title": get_real_name(name),
                "/Dest": [pdf_out.pages[-len(pdf_in.pages)], pikepdf.Name("/Fit")]
            })
        })
        pdf_out.root.Outlines.First.Parent = pdf_out.root.Outlines
        pdf_out.root.Outlines.Last = pdf_out.root.Outlines.First
    else:
        pdf_out.root.Outlines.Last.Next = pdf_out.make_indirect({
            "/Title": get_real_name(name),
            "/Parent": pdf_out.root.Outlines,
            "/Prev": pdf_out.root.Outlines.Last,
            "/Dest": [pdf_out.pages[-len(pdf_in.pages)], pikepdf.Name("/Fit")]
        })
        pdf_out.root.Outlines.Last = pdf_out.root.Outlines.Last.Next

    return len(pdf_in.pages)

def merge(pdf_streams, names, outpath, first_page):
    output = pikepdf.new()
    pgcounts = []

    for stream, name in tqdm.tqdm(zip(pdf_streams, names), total=len(names), desc="Merging PDFs"):
        pgcounts.append(append_pdf(output, stream, name))
    
    # add page numbering

    amount_of_contents = 0
    for amt, name in zip(pgcounts, names):
        if is_contents(name):
            amount_of_contents += amt
        else:
            break

    if amount_of_contents != 0:
        output.Root.PageLabels = {
            "/Nums": [
                0, {"/S": pikepdf.Name("/r")},
                amount_of_contents, {"/S": pikepdf.Name("/D"), "/St": first_page}
            ]
        }
    
    with tqdm.tqdm(total=100, desc="Writing PDF") as pbar:
        last = 0
        def update(x):
            nonlocal last
            g = x - last
            last = x
            pbar.update(g)

        output.save(outpath, progress=last)
