# NelsonDownloadPDF

This tool uses the myNelson internal API to download entire nelson eBooks as a PDF.

---
_warning: this tool is intended for **personal use only**, use of this tool to rip entire books and share them online is not endorsed by me in any way and any consequences from such actions are entirely your fault -- see the license for more information_

---

## Requirements

- python3

pip (requirements.txt):
- click
- colorama
- tqdm
- requests
- pikepdf


## Usage

To use the tool you should be comfortable with the dev tools in your browser.
Login to your myNelson account and go to the book you wish to download. Take note of the `pid` number in the URL.

![screenshot of pid parameter](/img/pid.png?raw=true)

This is the "Product ID"

Next, open up the dev tools and find the cookies for a request to `getexplorerinterface.json`.
Take note of the cookie `JSESSIONID` and `X-Oracle-BMC-LBS-Route`. These are your "Session ID" and "Server ID" respectively.

![chrome cookies panel](/img/cookie.png?raw=true)

(note this picture is a bit out of date and has the old name for the "server id")

Now run the `main.py` script, enter the values when prompted (or use the optional command line arguments), and sit back and relax while the script downloads everything.
By default the pdf will be called `output.pdf`, although you can change this with the `-o` command line option.

## Common errors
Q: I get a JSON error

A: Your session probably expired, try re-logging in and updating your session and server id

Q: I get invalid book structure 

A: Make sure the "tree index" is set to which position in the nelson viewer the pdfs are, in the picture above it would be 1 -- counting from zero the PDFs appear under the 2nd item in the first list. If you're getting this error, you can probably solve it
by passing `--tree-index 0` to the downloader.

Q: I get a `KeyError` when attempting to download an eBook.

A: The tool is only compatible with books that are distributed as PDFs in the nelson UI. Specifically, when you "open" the book there should be an interface similar to the pictures above which let you select per-chapter-section PDFs. For more information see issue #2.

## API reverse engineering information

Appears to have two main files, `https://www.mynelson.com/mynelson/service/explorer/getexplorerinterface.json` and `https://www.mynelson.com/mynelson/service/productdetail/links.json`.

The format appears to have `getexplorerinterface.json` tell you what the first column of the system contains, `links.json` gives you links to the actual content on their server.

Inside `getexplorerinterface.json`, there is the following format. To request it, give it a get parameter `productid`, with the id of the book you want.

```json
{
"Response": {
   "ProductInfo": {
      "title": book name,
      "accessUrl": <url>
   },
   ...
   "NavLevelTitleList": [<nav_title_list>, ...]
}
}
```

where

```javscript

<nav_title_list>: {
	"title": "name of thing",
	"navLevelId": <id>,
	"hasLinks": <true/false> are there links associated,
	"childList": [nav_title_list, ...]
}

<id>: integer
<url>: a url as a str

```

The `<id>`s from this file can be referenced in `links.json`, giving it the `productid` as with the other file, along with `levelid` equal to the `<id>`.

This returns something like

```json

{
"Response": {
"NavLinkTitleList": [<nav_link_list>, ...]
}
}
```

where

```javascript
<nav_link_list>: {
	"navLinkId": <id>,
	"title": "Title",
	"isDownloadable": <true/false>, can be ignored,
	"contentURL": <url> relative to the accessUrl in the ProductInfo of the other file,
	"description": null,
	"altContentURL": presumably an alternative to the contentURL,
	"associatedImgPath": an image representing the content,
	"fileType": <type>,
	...
}

<type>: one of "eBook", "PDF", "Weblink", and a few others.
```

For downloading files, one must obtain a token through the `https://www.mynelson.com/mynelson/service/openlink/getLinkURL.json` service.
This returns the following json, given get params `linkID` and `levelID`, taken from the respective ids.

```json
{
"Response": {
"ContentURL": <url>, same as in <nav_link_list>,
"ProductInfo": null,
"Token": str, add as get param token to final request for pdf
}
}
```

## License

This project is copyright (c) 2018 Matthew Mirvish under the MIT license.
