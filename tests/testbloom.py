import bloom

bloomFilter = bloom.BloomFilter()

for i in range(0,256):
    ip = '192.0.2.' + str(i)
    print(ip)
    bloomFilter.insertIP(ip);

for i in range(0,1000):
    ip = '2001:DB8::' + hex(i)[2:]
    print(ip)
    bloomFilter.insertIP(ip)
    
# Should be 1224.93088982
print(bloomFilter.estimate())