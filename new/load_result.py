import os
import json

# JSON file
f = open ("/home/anhp/Documents/coding/VEHI/hung_.json", "r")

# Reading from file
data = json.loads(f.read()) 

img_names = data.keys()
#print(len(img_names))

probs = []
for img_name in img_names:
    print(data[img_name])
    prob = []
    for obj in data[img_name]:
        score = obj[-1]
        prob.append(score)
    probs.append(prob)
    
print(probs[0][0])
