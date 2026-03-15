

with open('input.txt', 'r') as fichier_entree, open('output.txt', 'w') as fichier_sortie:

    id = 0
    for line in fichier_entree:
        processed_line = line.strip().split("\t")
        id = processed_line[0]
        name= processed_line[2]
        fichier_sortie.write( "{ id: " + id + ", name: \"" + name.strip() + "\" },\n" )
              

print("done")