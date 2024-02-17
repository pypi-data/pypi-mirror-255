# MoranKV

```python
from MoranKV import MoranKV


kivy_string = '''
Screen:
    BoxLayout:
        Text:
            text: "Hello World"'''

class App(MoranKV):
    ...


if __name__ == '__main__':
    App(string=kivy_string, app_name='Hello World').run()
```