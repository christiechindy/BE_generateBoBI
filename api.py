from flask import Flask, send_file, make_response
from flask import jsonify
from flask import request
from flask_cors import CORS
import fitx
import os
import json
import Pages_to_pagesr
import TitleOfWholeBooks
import MyRAKE
import WordEmbeddings as CountWordEmb
import math
from docxtpl import DocxTemplate

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./userinput"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def capitalize(index):
    return index[0].upper() + index[1:]

@app.route('/generate-rake', methods=['POST'])
def generateRake():
    filePDF = request.files["filePdf"]
    bookTitle = request.form.get("judul")
    jenis = request.form.get("adaJSON")

    if filePDF:
        PDFfilename = filePDF.filename
        savedPDFfile = os.path.join(app.config['UPLOAD_FOLDER'], PDFfilename)
        filePDF.save(savedPDFfile)

    if jenis=="1":
        fileJSON = request.files["fileJson"]
        JSONfilename = fileJSON.filename
        savedJSONfile = os.path.join(app.config['UPLOAD_FOLDER'], JSONfilename)
        fileJSON.save(savedJSONfile)
        with open(savedJSONfile, "r") as jsonFile:
            pages = json.load(jsonFile)
            pages_r = Pages_to_pagesr.convert(pages)
            titles = TitleOfWholeBooks.titleAndPageNumber(pages_r[0]["f"], pages_r[-1]["l"], savedPDFfile, pages_r)

    GENERATED = {}
    tmpTitle = ""

    for i in range(len(pages)):
        for j in range(pages[i]["f"], pages[i]["l"]+1):
            page_text = fitx.extract_text_from_a_page(savedPDFfile, j+pages[i]["d"]-1)
            rakeIndex = MyRAKE.all(page_text)

            for rakeIdx in rakeIndex:
                rakeMark = rakeIndex[rakeIdx]
                rakeIndex[rakeIdx] = {"rake": rakeMark}

                # compute its mark against the word embeddings
                cosMark = 0
                if (len(titles[j]) != 0):
                    for k in range(len(titles[j]) + 1):
                        if (k == len(titles[j])): # klo iteration trkhr mi, compare ke bookTitle
                            Cos_AvF = CountWordEmb.count_CosAvF(rakeIdx, bookTitle)
                            if not math.isnan(Cos_AvF):
                                cosMark += abs(Cos_AvF)
                        else:
                            tmpTitle = titles[j][k][1] if titles[j][k] else tmpTitle
                            if (tmpTitle != ""):
                                Cos_AvF = CountWordEmb.count_CosAvF(rakeIdx, tmpTitle)
                                if not math.isnan(Cos_AvF):
                                    cosMark += abs(Cos_AvF)
                else: # klo kosong (tidak ada judul di page tsb, maka pake last title saja)
                    if tmpTitle:
                        Cos_AvF = CountWordEmb.count_CosAvF(rakeIdx, tmpTitle)
                        if not math.isnan(Cos_AvF):
                            cosMark += abs(Cos_AvF)
                    Cos_AvF = CountWordEmb.count_CosAvF(rakeIdx, bookTitle)
                    if not math.isnan(Cos_AvF):
                        cosMark += abs(Cos_AvF)
                rakeIndex[rakeIdx]["cos"] = cosMark

                # compute also the point of its capitalization
                capAmnt = MyRAKE.countCapitalLetters(rakeIdx)
                rakeIndex[rakeIdx]["cap"] = capAmnt

                # count the total sum of them (RAKE + cos + cap)
                total = rakeMark + (cosMark*1) + (capAmnt*8)
                rakeIndex[rakeIdx]["total"] = total
            
            # rank based on the total marks
            sortedRakeIndex = dict(sorted(rakeIndex.items(), key=lambda item: item[1]["total"], reverse=True))
            convert_to_list = list(sortedRakeIndex.items())
            totalIndex = len(sortedRakeIndex)
            numberstotake = 20 if totalIndex>20 else totalIndex
            topN = convert_to_list[:numberstotake]
            topNindexes = dict(topN)
            print(f"Page {j}")
            print(topNindexes)

            for topNindex in topNindexes:
                if topNindex.lower() not in [ndpl.lower() for ndpl in GENERATED]:
                    idx__ = next((key for key,value in GENERATED.items() if MyRAKE.splitEachWord(topNindex) == MyRAKE.splitEachWord(key)), None)
                    if idx__ is None:
                        GENERATED[topNindex] = [j]
                    else: #klo sdh ada di GENERATED
                        if "-" in topNindex: 
                            GENERATED[idx__].append(j) 
                        # klo "-" in GENERATED[idx__] brti cckmi, jgnmi gntiki

                else: # kalau sdh ada mi di GENERATED
                    idx = next((key for key,value in GENERATED.items() if key.lower() == topNindex.lower()), None)
                    # cek! kalau lebih kapital ki, gnti dgn yg ini
                    if (MyRAKE.sum_ascii(topNindex) < MyRAKE.sum_ascii(idx)):
                        GENERATED[idx].append(j)
                        continue

    SortedGENERATED = dict(sorted(GENERATED.items(), key=lambda item: item[0].lower()))

    TEXT = ""
    for element in SortedGENERATED:
        TEXT += f"{capitalize(element)}, "
        for lengthh, page in enumerate(SortedGENERATED[element]):
            TEXT += f"{page}"
            if lengthh != len(SortedGENERATED[element])-1:
                TEXT += ", "
        TEXT += "\n"

    generatedPath = "generatedFile.docx"
    doc = DocxTemplate("TEMPLATE.docx")
    doc.render({"content": TEXT})
    doc.save(generatedPath)

    try:
        os.remove(savedPDFfile)
        os.remove(savedJSONfile)
    except:
        print(f"Failed deleting user files")

    # Send the file as a response
    return send_file(generatedPath, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1313)