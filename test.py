import datetime

with open('res.txt', 'w') as f:
    f.write('Hello, World!')
    f.write(f'\n{datetime.datetime.now()}')

print('Done script')