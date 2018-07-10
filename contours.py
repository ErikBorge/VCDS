import math

def eliminate_child_rects(rects):
    rectDict = dict()
    newRects = []
    has_child = False
    rects = list(set(rects))
    for i in range(len(rects)):
        r1 = rects[i]
        for j in range(len(rects)):
            r2 = rects[j]
            if is_same_rectangle(r1, r2):
                print("R1:",r1, "R2:", r2, " same!")
                continue
            if is_contains_rectangle(rects[i], rects[j]):
                print(rects[i], "contains", rects[j])
                if i not in rectDict:
                    rectDict[i] = [rects[j]]
                else:
                    rectDict[i].append(rects[j])
            elif is_similar_rectangle(r1, r2, 5):
                print(r1, "is similar to", r2)
                eliminatedR = None
                if get_bigger_rect(r1, r2) == r1:
                    index = i
                    eliminatedR = r2
                else:
                    index = j
                    eliminatedR = r1
                print("index:", i, "eliminatedR:", eliminatedR)
                if index not in rectDict:
                    rectDict[index] = [eliminatedR]
                else:
                    rectDict[index].append(eliminatedR)
    print(rects)
    print(rectDict)
    for (k, v) in rectDict.items():
        for r in v:
            if r in rects:
                rects.remove(r)
    for r in rects:
        newRects.append(r)
    return newRects
