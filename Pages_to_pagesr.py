def convert(pages):
    pages_r = []
    now = {}

    for i in range(len(pages)):
        if i == 0:
            now["f"] = pages[i]["f"] + pages[i]["d"]
            now["d"] = pages[i]["d"]
            now["l"] = pages[i]["l"] + pages[i]["d"]
            continue

        if pages[i]["d"] != pages[i-1]["d"]:
            now["l"] = pages[i]["f"] + pages[i]["d"] - 1
            pages_r.append(now)
            now = {}
            now["f"] = pages[i]["f"] + pages[i]["d"]
            now["d"] = pages[i]["d"]
            now["l"] = pages[i]["l"] + pages[i]["d"]
        else:
            now["l"] = pages[i]["l"] + pages[i]["d"]

    pages_r.append(now)

    return pages_r