from jacpy.hash import hashUtils

items = hashUtils.dirItems('C:/Users/alber/Desktop/BACKUP ABRIL 2022', hashUtils.DirItemPolicy.AllAlphabetic, 0, 2)

print(items)