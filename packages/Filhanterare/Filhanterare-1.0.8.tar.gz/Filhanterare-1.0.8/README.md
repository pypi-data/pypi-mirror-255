# Filhanterare

```python
from Filhanterare import FileManager

fm = FileManager(app_name='My App')
fm.set_file('my_file.txt', 'Hello World!')

print(fm.get_file('my_file.txt'))
```