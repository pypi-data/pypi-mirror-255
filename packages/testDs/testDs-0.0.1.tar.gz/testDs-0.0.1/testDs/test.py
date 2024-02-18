from tools import calculator

def test_calculator():
    a = 5
    b = 10
    v = calculator(a, b, operation = '*')
    print(v)
    assert v == 50, "Not correct"