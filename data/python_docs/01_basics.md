# Python 기초: 변수, 자료형, 연산자

## 변수와 자료형

Python은 동적 타입 언어로, 변수 선언 시 타입을 명시하지 않아도 됩니다.

```python
# 정수 (int)
age = 25
count = -10

# 실수 (float)
pi = 3.14
temperature = -2.5

# 문자열 (str)
name = "Alice"
greeting = 'Hello, World!'

# 불리언 (bool)
is_active = True
is_done = False

# None
result = None
```

## 문자열 다루기

```python
s = "Hello, Python!"

# 길이
print(len(s))          # 14

# 인덱싱 (0부터 시작)
print(s[0])            # H
print(s[-1])           # !

# 슬라이싱
print(s[0:5])          # Hello
print(s[7:])           # Python!

# 메서드
print(s.upper())       # HELLO, PYTHON!
print(s.lower())       # hello, python!
print(s.replace("Python", "World"))  # Hello, World!
print(s.split(", "))   # ['Hello', 'Python!']

# f-string (Python 3.6+)
name = "Bob"
age = 30
print(f"이름: {name}, 나이: {age}")
```

## 리스트 (List)

순서가 있고, 변경 가능한 컬렉션입니다.

```python
fruits = ["apple", "banana", "cherry"]

# 접근
print(fruits[0])       # apple
print(fruits[-1])      # cherry

# 추가
fruits.append("mango")       # 끝에 추가
fruits.insert(1, "grape")    # 인덱스 위치에 삽입

# 제거
fruits.remove("banana")      # 값으로 제거
popped = fruits.pop()        # 마지막 요소 제거 및 반환
del fruits[0]                # 인덱스로 제거

# 정렬
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort()               # 원본 수정
sorted_nums = sorted(numbers) # 새 리스트 반환

# 리스트 컴프리헨션
squares = [x**2 for x in range(1, 6)]  # [1, 4, 9, 16, 25]
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
```

## 딕셔너리 (Dictionary)

키-값 쌍으로 이루어진 컬렉션입니다.

```python
person = {
    "name": "Alice",
    "age": 25,
    "city": "Seoul"
}

# 접근
print(person["name"])            # Alice
print(person.get("email", "없음"))  # 없음 (키가 없을 때 기본값)

# 수정/추가
person["age"] = 26
person["email"] = "alice@example.com"

# 삭제
del person["city"]

# 순회
for key, value in person.items():
    print(f"{key}: {value}")

# 딕셔너리 컴프리헨션
squared = {x: x**2 for x in range(1, 6)}
```

## 자주 하는 실수

```python
# ❌ 잘못된 예: 리스트를 복사할 때 참조 복사
a = [1, 2, 3]
b = a        # b는 a와 같은 객체를 가리킴
b.append(4)
print(a)     # [1, 2, 3, 4] - a도 변경됨!

# ✅ 올바른 예: 얕은 복사
b = a.copy()   # 또는 b = a[:]
b.append(4)
print(a)     # [1, 2, 3] - a는 그대로

# ❌ 잘못된 예: 문자열과 숫자 결합
age = 25
# print("나이: " + age)  # TypeError!

# ✅ 올바른 예
print("나이: " + str(age))
print(f"나이: {age}")
```
