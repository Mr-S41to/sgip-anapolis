from decimal import Decimal

a = Decimal("20,3".replace(",", "."))
b = Decimal("19,7".replace(",", "."))
c = a + b

print(c)