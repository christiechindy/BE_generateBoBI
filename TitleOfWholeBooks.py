import fitx
import re

def getTitleOfAPage(book_path, pageNumber_whole, previousDigit, previous2ndDigit):
    page_text = fitx.extract_text_with_mupdf(book_path, pageNumber_whole-1, pageNumber_whole)

    lines = page_text.split("\n")
    prev = previousDigit
    firstnumber = 1
    prevSec = previous2ndDigit
    secondnumber = 1

    res = []
    for line in lines:
        regex = re.findall(r"^([1-9]\d*\.[\d\.]+)\s*([A-Z].+)", line)
        regex_init = re.findall(r"^\d+", line)
        regex_second = re.findall(r"^\d+\.(\d*)", line)
        firstnumber = int(regex_init[0]) if len(regex_init) > 0 else firstnumber
        try:
            secondnumber = int(regex_second[0])
        except:
            pass

        if (regex != [] and secondnumber==1 and firstnumber==prev+1):
            prevSec = 1

        if (regex != []) and (firstnumber == prev or firstnumber == prev+1) and (secondnumber == prevSec or secondnumber == prevSec+1):
            prevSec = secondnumber
            prev = firstnumber
            res.append(regex[0])
    
    return res, prev, prevSec

# first_page -> what page is the page number 1
# last_page  -> the last absolute content page
# pages_r    -> array of dict {"f", "l", "d"}
#               f: absolute first page number,
#               l: absolute last page number,
#               d: difference between absolute and labeled page number
def titleAndPageNumber(first_page, last_page, book_path, pages_r):
    _prev = 1
    _prevSec = 1

    p_idx = 0
    all = [[] for i in range(pages_r[-1]["l"] - pages_r[-1]["d"] + 1)]
    for i in range(first_page, last_page+1):
        res, prev, prevSec = getTitleOfAPage(book_path, i, _prev, _prevSec)
        _prev = prev 
        _prevSec = prevSec
        if (i > pages_r[p_idx]["l"]):
            p_idx += 1
        num = i - pages_r[p_idx]["d"]
        all[num] = res

    return all