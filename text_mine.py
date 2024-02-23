#%%
from pathlib import Path
import fitz
import re
from scrape import DOWNLOAD_PATH
from tqdm import tqdm
#%%

# pat = re.compile("[dD]issertation")
# pat = re.compile("previous")
pat = re.compile("([Pp]revious|[Oo]ther) [tT]hes[ie]s")
for pdf_file in Path(DOWNLOAD_PATH).glob("*.pdf"):
    doc = fitz.open(pdf_file) # open a document
    for pagenum,page in enumerate(doc):
        text = page.get_text()
        # print(text)
        if hits:=pat.finditer(text):
            for search in hits: 
                print(pdf_file,pagenum)
                start,end = search.span(0)
                print(f"\t{text[start-100:end+100]}")

# %%
