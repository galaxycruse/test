# Python 함수

## 기본 함수 정의

```python
def greet(name):
    return f"안녕하세요, {name}님!"

print(greet("Alice"))  # 안녕하세요, Alice님!
```

## 매개변수 종류

```python
# 기본값 매개변수
def power(base, exponent=2):
    return base ** exponent

print(power(3))     # 9 (3^2)
print(power(3, 3))  # 27 (3^3)

# 키워드 인수
def introduce(name, age, city="서울"):
    return f"{name}({age}세)은 {city} 거주"

print(introduce(age=25, name="Bob"))  # 순서 무관

# 가변 인수 (*args)
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4, 5))  # 15

# 키워드 가변 인수 (**kwargs)
def show_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

show_info(name="Alice", age=25, city="Seoul")
```

## 람다 함수

```python
# lambda: 간단한 익명 함수
square = lambda x: x ** 2
print(square(5))  # 25

# sorted의 key로 활용
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
sorted_students = sorted(students, key=lambda s: s[1], reverse=True)
# [('Bob', 92), ('Alice', 85), ('Charlie', 78)]

# map, filter와 함께
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))   # [2, 4, 6, 8, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]
```

## 스코프 (Scope)

```python
x = 10  # 전역 변수

def func():
    x = 20  # 지역 변수 (전역 x와 별개)
    print(x)  # 20

func()
print(x)  # 10 (전역 x는 그대로)

# global 키워드
def increment():
    global x
    x += 1

increment()
print(x)  # 11
```

## 재귀 함수

```python
def factorial(n):
    if n <= 1:      # 기저 조건 (Base Case) - 필수!
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120

# 피보나치 수열
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))  # 55
```

## 내장 함수 자주 쓰는 것

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

print(len(numbers))    # 8
print(max(numbers))    # 9
print(min(numbers))    # 1
print(sum(numbers))    # 31
print(sorted(numbers)) # [1, 1, 2, 3, 4, 5, 6, 9]

# type, isinstance
print(type(42))        # <class 'int'>
print(isinstance(42, int))  # True

# zip, enumerate (루프에서 자주 활용)
names = ["A", "B", "C"]
for i, name in enumerate(names, start=1):
    print(f"{i}. {name}")
```

## 자주 하는 실수

```python
# ❌ 기본값으로 가변 객체(리스트) 사용
def add_item(item, lst=[]):  # 위험!
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - 이전 호출 결과가 유지됨!

# ✅ 올바른 방법
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

# ❌ 재귀 기저 조건 누락
# def infinite_recursive(n):
#     return infinite_recursive(n-1)  # RecursionError!
```
