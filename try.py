from xml.etree import ElementTree as ET

'''
copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
it basically walks your tree and adds spaces and newlines so the tree is
printed in a nice way
'''


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


'''
function to build an example tree containing cars and ships
vehicles is the root node
'''


def buildTree():
    vehicles = ET.Element("vehicles")

    cars = ET.SubElement(vehicles, "cars")
    cars.set("Type", "American")

    car1 = ET.SubElement(cars, "car")
    car1.text = "Ford Mustang"

    car2 = ET.SubElement(cars, "car")
    car2.text = "Dodge Viper"

    ships = ET.SubElement(vehicles, "ships")
    ships.set("Type", "sunken")

    ship1 = ET.SubElement(ships, "ship")
    ship1.text = "Titanic"

    indent(vehicles)

    tree = ET.ElementTree(vehicles)

    tree.write("vehicle_file.xml", xml_declaration=True, encoding='utf-8', method="xml")


'''
main function, so this program can be called by python program.py
'''
if __name__ == "__main__":
    buildTree()