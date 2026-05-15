# Python 제어문: 조건문과 반복문

## 조건문 (if / elif / else)

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"학점: {grade}")  # 학점: B
```

### 삼항 연산자 (조건 표현식)

```python
x = 10
result = "양수" if x > 0 else "음수 또는 0"
print(result)  # 양수
```

### 논리 연산자

```python
age = 20
has_id = True

# and, or, not
if age >= 18 and has_id:
    print("입장 가능")

if not has_id:
    print("신분증이 없습니다")
```

## 반복문 (for / while)

### for 문

```python
# 리스트 순회
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# range 사용
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):    # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8 (step=2)
    print(i)

# enumerate: 인덱스와 값을 함께
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# zip: 두 리스트를 병렬로
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

### while 문

```python
count = 0
while count < 5:
    print(count)
    count += 1

# 무한 루프 탈출
while True:
    user_input = input("종료하려면 'q'를 입력: ")
    if user_input == 'q':
        break
```

### break, continue, pass

```python
# break: 루프 즉시 종료
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: 현재 반복을 건너뜀
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9

# pass: 아무것도 하지 않음 (자리 채우기)
for i in range(5):
    if i == 3:
        pass  # 나중에 구현 예정
    print(i)
```

## 중첩 루프

```python
# 구구단 2단 ~ 3단
for dan in range(2, 4):
    for i in range(1, 10):
        print(f"{dan} x {i} = {dan * i}")
    print()

# 리스트 컴프리헨션으로 2D 리스트
matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

## 자주 하는 실수

```python
# ❌ while 무한 루프 (탈출 조건 없음)
# count = 0
# while count < 5:
#     print(count)
#     # count += 1 를 빠뜨리면 무한 루프!

# ❌ for 루프 안에서 리스트 수정
nums = [1, 2, 3, 4, 5]
# for n in nums:
#     if n % 2 == 0:
#         nums.remove(n)  # 위험! 순회 중 리스트 수정

# ✅ 올바른 방법
nums = [n for n in nums if n % 2 != 0]

# ❌ range에서 흔한 실수: 마지막 값 포함 여부
for i in range(5):
    print(i)  # 0~4 출력, 5는 포함 안됨
```
