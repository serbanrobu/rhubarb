from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple


@dataclass(frozen=True)
class App:
    fun: Expr
    arg: Expr


@dataclass(frozen=True)
class Lam:
    var: str = field(compare=False)
    type: Expr
    body: Expr


@dataclass(frozen=True)
class Pi:
    var: str = field(compare=False)
    type: Expr
    body: Expr


@dataclass
class Unknown:
    pass


@dataclass(frozen=True)
class Var:
    index: int


Expr = App | Lam | Pi | Unknown | Var


Context = List[Tuple[str, Expr]]


class Assoc(Enum):
    LEFT = 0
    RIGHT = 1
    BOTH = 2


def show(expr: Expr, ctx: Context = [], assoc: Optional[Assoc] = Assoc.BOTH) -> str:
    match expr:
        case App(fun, arg):
            result = f'{show(fun, ctx, Assoc.LEFT)} {show(arg, ctx, None)}'

            match assoc:
                case Assoc.LEFT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Lam(var, type, body):
            result = f'λ ({var} : {show(type, ctx)}). {show(body, [(var, type), *ctx])}'

            match assoc:
                case Assoc.RIGHT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Pi(var, type, body):
            result = f'Π ({var} : {show(type, ctx)}). {show(body, [(var, type), *ctx])}'

            match assoc:
                case Assoc.RIGHT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Unknown():
            return '?'

        case Var(index):
            name, _ = ctx[index]
            return name


def shift(expr: Expr, n: int, cutoff: int = 0) -> Expr:
    match expr:
        case App(fun, arg):
            return App(shift(fun, n, cutoff), shift(arg, n, cutoff))

        case Lam(var, type, body):
            return Lam(var, shift(type, n, cutoff), shift(body, n, cutoff + 1))

        case Pi(var, type, body):
            return Pi(var, shift(type, n, cutoff), shift(body, n, cutoff + 1))

        case Unknown():
            return expr

        case Var(index):
            if index < cutoff:
                return expr
            else:
                return Var(index + n)


def substitute(expr: Expr, val: Expr, i: int = 0) -> Expr:
    match expr:
        case App(fun, arg):
            return App(substitute(fun, val, i), substitute(arg, val, i))

        case Lam(var, type, body):
            return Lam(
                var,
                substitute(type, val, i),
                substitute(body, shift(val, 1), i + 1),
            )

        case Pi(var, type, body):
            return Pi(
                var,
                substitute(type, val, i),
                substitute(body, shift(val, 1), i + 1),
            )

        case Unknown():
            return expr

        case Var(index):
            return val if index == i else expr


def value(expr: Expr) -> Expr:
    match expr:
        case App(fun, arg):
            match value(fun):
                case Lam(_, _, body):
                    return value(shift(substitute(body, shift(arg, 1)), -1))

                case _:
                    raise Exception('Expecting a lambda')

        case _:
            return expr


def reduce(expr: Expr) -> Expr:
    match value(expr):
        case App(fun, arg):
            return App(reduce(fun), reduce(arg))

        case Lam(var, type, body):
            return Lam(var, reduce(type), reduce(body))

        case Pi(var, type, body):
            return Pi(var, reduce(type), reduce(body))

        case _:
            return expr


def show_context(ctx: Context) -> str:
    match ctx:
        case [(var, type), *tail]:
            return f'{show_context(tail)}{var} : {show(type, tail)}\n'

        case _:
            return ''


def type_check(expr: Expr, ctx: Context = []) -> Expr:
    match expr:
        case App(fun, arg):
            fun_type = type_check(fun, ctx)
            match fun_type:
                case Pi(var, type, body):
                    match type_check(type, ctx):
                        case Unknown():
                            pass

                        case other:
                            raise Exception(
                                f'\n{show_context(ctx)}Expecting a type, found {show(type, ctx)} : {show(other, ctx)}'
                            )

                    arg_type = type_check(arg, ctx)

                    if not is_subexpr(type, arg_type):
                        raise Exception(
                            f'\n{show_context(ctx)}Expecting a {show(type, ctx)}, found {show(arg, ctx)} : {show(arg_type, ctx)}'
                        )

                    return shift(substitute(body, shift(arg, 1)), -1)

                case other:
                    raise Exception(
                        f'\n{show_context(ctx)}Expecting a function, found {show(other, ctx)} : {show(fun_type, ctx)}'
                    )

        case Lam(var, type, body):
            type_check(type, ctx)

            return Pi(
                var,
                type,
                type_check(body, [(var, type), *ctx]),
            )

        case Pi(var, type, body):
            type_check(type, ctx)
            type_check(body, [(var, type), *ctx])
            return Unknown()

        case Unknown():
            return expr

        case Var(index):
            _, type = ctx[index]
            return shift(type, int(index) + 1)


def is_subexpr(expr1: Expr, expr2: Expr) -> bool:
    match expr1, expr2:
        case App(fun1, arg1), App(fun2, arg2):
            return is_subexpr(fun1, fun2) and is_subexpr(arg1, arg2)

        case Lam(_, type1, body1), Lam(_, type2, body2):
            return is_subexpr(type1, type2) and is_subexpr(body1, body2)

        case Pi(_, type1, body1), Pi(_, type2, body2):
            return is_subexpr(type1, type2) and is_subexpr(body1, body2)

        case Unknown(), _:
            return True

        case _:
            return expr1 == expr2


Value = Any | Callable[[Any], Any]

Env = List[Value]


def eval(expr: Expr, env: Env = []) -> Value:
    match expr:
        case App(fun, arg):
            f = eval(fun, env)
            return None if f is None else f(eval(arg, env))

        case Lam(_, _, body):
            return lambda val: eval(body, [val, *env])

        case Pi(_, _, _):
            return None

        case Unknown():
            return None

        case Var(index):
            return env[index]
