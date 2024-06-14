Usando key è stato generato il parametro output, contiene la flag rimescolata in qualche modo, nel codice sotto c'è sia il codice della challenge che quello usato per il solve.

```
#!/usr/bin/env python3

import os

import random

  

output = "fsa3n_yt0yt_e1_tn_9_ctpf_1n54s1_psui8op{}g4s_rcr4l1n4e3wllrs16e_3ea_n"

key = {'f': 18, 'l': 58, 'a': 22, 'g': 30, '{': 33, '4': 63, 'p': 68, 'r': 47, 'e': 6, 'n': 56, 't': 5, 'y': 40, '_': 17, '1': 30, 's': 53, 'c': 54, 'o': 63, '0': 67, 'w': 3, '3': 20, 'i': 26, 'u': 37, '6': 16, '5': 26, '9': 63, '8': 50, '}': 26}

  

flag = "ciao"

keyTest = {'c': 2, 'i': 1, 'a': 3, 'o': 1}

  

def spin(w, k):

k = k % len(w)

return w[-k:] + w[:-k]

  

def reverseSpin(w, k):

k = k % len(w)

print(f'{w = }')

print(f'{k = }')

print("returning: " + w[k:] + w[:k])

return w[k:] + w[:k]

  

def encrypt_or_hash(w, key):

for i in range(1, len(w)):

w = w[:i] + spin(w[i:], key[w[i-1]])

print(f'{w = }')

return w

  

#output = encrypt_or_hash(flag, key)

  

print(f'{key = }')

print(f'{output = }\n')

  

def decrypt(output, key):

for i in range(len(output) - 1, 0, -1):

output = output[:i] + reverseSpin(output[i:], key[output[i-1]])

print(f'{output = }')

return output

  

print(f'{decrypt(output, key) = }\n')
```