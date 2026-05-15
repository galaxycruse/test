# Python 객체 지향 프로그래밍 (OOP)

## 클래스와 객체

```python
class Dog:
    # 클래스 변수 (모든 인스턴스가 공유)
    species = "Canis familiaris"

    def __init__(self, name, age):
        # 인스턴스 변수
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name}이(가) 왈왈!"

    def __str__(self):
        return f"Dog(name={self.name}, age={self.age})"

    def __repr__(self):
        return f"Dog('{self.name}', {self.age})"

# 인스턴스 생성
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.bark())          # Buddy이(가) 왈왈!
print(dog1)                 # Dog(name=Buddy, age=3)
print(Dog.species)          # Canis familiaris
```

## 상속 (Inheritance)

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("서브클래스에서 구현 필요")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

class Dog(Animal):
    def speak(self):
        return f"{self.name}: 왈왈!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 야옹~"

# 다형성
animals = [Dog("Buddy"), Cat("Whiskers"), Dog("Max")]
for animal in animals:
    print(animal.speak())

# super() 사용
class GuideDog(Dog):
    def __init__(self, name, owner):
        super().__init__(name)  # 부모 __init__ 호출
        self.owner = owner

    def speak(self):
        return super().speak() + f" (안내견, 주인: {self.owner})"
```

## 캡슐화

```python
class BankAccount:
    def __init__(self, balance=0):
        self.__balance = balance  # private 변수 (name mangling)

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return True
        return False

    @property
    def balance(self):          # getter
        return self.__balance

    @balance.setter
    def balance(self, value):   # setter
        if value >= 0:
            self.__balance = value

account = BankAccount(1000)
account.deposit(500)
print(account.balance)    # 1500
# print(account.__balance)  # AttributeError
```

## 클래스 메서드 / 정적 메서드

```python
class MathHelper:
    PI = 3.14159

    @classmethod
    def circle_area(cls, radius):
        return cls.PI * radius ** 2

    @staticmethod
    def is_even(number):
        return number % 2 == 0

print(MathHelper.circle_area(5))  # 78.53975
print(MathHelper.is_even(4))      # True
```

## 데이터클래스 (Python 3.7+)

```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    age: int
    scores: list = field(default_factory=list)

    def average_score(self):
        return sum(self.scores) / len(self.scores) if self.scores else 0

s = Student("Alice", 20, [85, 92, 78])
print(s)               # Student(name='Alice', age=20, scores=[85, 92, 78])
print(s.average_score())  # 85.0
```

## 자주 하는 실수

```python
# ❌ self를 빠뜨리는 실수
class Counter:
    count = 0

    def increment():  # self 누락!
        Counter.count += 1

# ✅ 올바른 방법
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

# ❌ 클래스 변수와 인스턴스 변수 혼동
class Foo:
    items = []  # 클래스 변수 - 모든 인스턴스가 공유!

    def add(self, item):
        self.items.append(item)  # 클래스 변수가 수정됨

# ✅ 인스턴스 변수로 선언
class Foo:
    def __init__(self):
        self.items = []  # 각 인스턴스가 독립적으로 가짐
```
