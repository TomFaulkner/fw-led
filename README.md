# Framework LED Matrix

## Usage:

```shell
python3 main.py
```

## Adjust brightness:

Use the path provided when starting the program to adjust the brightness of the LED matrix.
Values are a percentage of the maximum (255) brightness.
In my experience, absolute brightness of less than 10 is not visible, if on at all.
So, two percent or less is probably not visible.

```shell
echo 100 > $path/brightness
```

Before running again, delete any files from the $path above.
For safety the contents aren't automatically deleted.
