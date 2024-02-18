This is just a little package I made for my GMP teacher.

To print things with style you can use the printing class
```python
import gmp
style = gmp.printing("purple4", "blue")
print(style.print([1,2,3], ["hello", "world"], ...))
```

If you feel like rainbow you can use the rainbow class with lolcat!
```python
import gmp
color = gmp.rainbow(False)
print(color.lolcat("I love rainbows"))

color = gmp.rainbow(True)
print(color.lolcat("Lolcat is super cool"))
```