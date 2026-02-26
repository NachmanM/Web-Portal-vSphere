import json

def main():
    dropdown_items = []
    for n in range(5):
        dropdown_items.append({"name": f"item-{n}",
                               "code": f"ITEM-{n}"})

    print(json.dumps(dropdown_items))

if __name__ =='__main__':
    main()