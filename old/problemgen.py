import random

NB_BLOCKS = 5

blocks = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9']
random.shuffle(blocks)
blocks = blocks[:NB_BLOCKS]

nb_piles = random.randint(1, NB_BLOCKS)  # Number of different piles. 1 to NB_BLOCKS inclusive
print("nb_piles:", nb_piles)

piles = []
for nb in range(nb_piles):
    piles.append([blocks[nb]]) # Each pile has at least one element

for nb2 in range(nb+1, NB_BLOCKS):
    piles[random.randint(0, nb_piles-1)].append(blocks[nb2])

# Pick two positions with distance at least 2 (so they're not on top of each other already)
while True:
    posblock1 = random.randint(0, NB_BLOCKS-1)
    posblock2 = random.randint(0, NB_BLOCKS-1)
    if posblock1 > posblock2+1 or posblock2 > posblock1+1:
        break

flattenedlist = sum(piles, [])
print(flattenedlist)
problem = [flattenedlist[posblock1], flattenedlist[posblock2]] 


random.shuffle(piles)
print("state:", [" on ".join(p)+" on table" for p in piles], "| goal:", " on ".join(problem))






