# Python 예외처리와 파일 입출력

## 예외처리 (try / except)

```python
# 기본 구조
try:
    result = 10 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다.")

# 여러 예외 처리
try:
    value = int(input("숫자 입력: "))
    result = 100 / value
except ValueError:
    print("올바른 숫자가 아닙니다.")
except ZeroDivisionError:
    print("0은 입력할 수 없습니다.")
except Exception as e:
    print(f"예상치 못한 오류: {e}")
else:
    print(f"결과: {result}")  # 예외가 없을 때 실행
finally:
    print("항상 실행됩니다.")  # 예외 여부와 무관
```

## 예외 발생시키기

```python
def divide(a, b):
    if b == 0:
        raise ValueError("나누는 수는 0이 될 수 없습니다.")
    return a / b

# 커스텀 예외
class InsufficientFundsError(Exception):
    def __init__(self, amount, balance):
        self.amount = amount
        self.balance = balance
        super().__init__(f"잔액 부족: {balance}원 있지만 {amount}원 출금 시도")

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(amount, balance)
    return balance - amount

try:
    new_balance = withdraw(1000, 1500)
except InsufficientFundsError as e:
    print(e)  # 잔액 부족: 1000원 있지만 1500원 출금 시도
```

## 자주 발생하는 예외 종류

| 예외 | 발생 상황 |
|------|---------|
| ValueError | 잘못된 값 (int("abc")) |
| TypeError | 잘못된 타입 연산 ("a" + 1) |
| IndexError | 인덱스 범위 초과 ([1,2][5]) |
| KeyError | 딕셔너리에 없는 키 접근 |
| AttributeError | 없는 속성/메서드 접근 |
| FileNotFoundError | 파일 없음 |
| ZeroDivisionError | 0으로 나누기 |
| ImportError | 모듈 import 실패 |

## 파일 입출력

```python
# 파일 쓰기
with open("example.txt", "w", encoding="utf-8") as f:
    f.write("첫 번째 줄\n")
    f.write("두 번째 줄\n")

# 파일 읽기
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 전체 읽기
    # lines = f.readlines()     # 줄 단위 리스트
    # line = f.readline()       # 한 줄 읽기

# 줄 단위로 읽기
with open("example.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # \n 제거

# 파일 추가 (append)
with open("example.txt", "a", encoding="utf-8") as f:
    f.write("세 번째 줄\n")
```

## with 문과 컨텍스트 매니저

```python
# with 문을 사용하면 자동으로 파일이 닫힘
# try/finally 없이도 안전한 자원 관리

# ❌ 비권장 방법
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()

# ✅ 권장 방법
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
# 블록을 벗어나면 자동으로 닫힘
```

## 자주 하는 실수

```python
# ❌ 너무 넓은 예외 처리 (버그 숨김)
try:
    do_something()
except Exception:
    pass  # 모든 예외를 무시 - 디버깅이 매우 어려워짐

# ✅ 구체적인 예외만 처리
try:
    do_something()
except SpecificError as e:
    logger.error(f"오류 발생: {e}")
    raise  # 또는 적절한 처리

# ❌ 인코딩 미지정
# with open("file.txt", "r") as f:  # 시스템 기본 인코딩 사용 (위험)

# ✅ 항상 인코딩 명시
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```
