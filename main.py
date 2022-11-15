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
class Let:
    var: str = field(compare=False)
    term: Expr
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


Expr = App | Lam | Let | Pi | Unknown | Var


Context = List[Tuple[str, Expr, Optional[Expr]]]


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
            result = f'λ ({var} : {show(type, ctx)}). {show(body, [(var, type, None), *ctx])}'

            match assoc:
                case Assoc.RIGHT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Let(var, term, body):
            result = f'let {var} ≡ {show(term, ctx)} in {show(body, [(var, Unknown(), term), *ctx])}'

            match assoc:
                case Assoc.RIGHT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Pi(var, type, body):
            result = f'Π ({var} : {show(type, ctx)}). {show(body, [(var, type, None), *ctx])}'

            match assoc:
                case Assoc.RIGHT | Assoc.BOTH:
                    return result

                case _:
                    return f'({result})'

        case Unknown():
            return '?'

        case Var(index):
            name, _, _ = ctx[index]
            return name


def shift(expr: Expr, n: int, cutoff: int = 0) -> Expr:
    match expr:
        case App(fun, arg):
            return App(shift(fun, n, cutoff), shift(arg, n, cutoff))

        case Lam(var, type, body):
            return Lam(var, shift(type, n, cutoff), shift(body, n, cutoff + 1))

        case Let(var, term, body):
            return Let(var, shift(term, n, cutoff), shift(body, n, cutoff + 1))

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

        case Let(var, term, body):
            return Let(
                var,
                substitute(term, val, i),
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


def value(expr: Expr, ctx: Context = []) -> Expr:
    match expr:
        case App(fun, arg):
            match value(fun, ctx):
                case Lam(_, _, body):
                    return value(shift(substitute(body, shift(arg, 1)), -1), ctx)

                case _:
                    raise Exception('Expecting a lambda')

        case Let(var, term, body):
            return value(body, [(var, Unknown(), term), *ctx])

        case Var(index):
            _, _, term = ctx[index]
            return expr if term is None else shift(term, int(index) + 1)

        case _:
            return expr


def reduce(expr: Expr, ctx: Context = []) -> Expr:
    match value(expr, ctx):
        case App(fun, arg):
            return App(reduce(fun, ctx), reduce(arg, ctx))

        case Lam(var, type, body):
            return Lam(var, reduce(type, ctx), reduce(body, [(var, type, None), *ctx]))

        case Pi(var, type, body):
            return Pi(var, reduce(type, ctx), reduce(body, [(var, type, None), *ctx]))

        case _:
            return expr


def show_context(ctx: Context) -> str:
    match ctx:
        case [(var, type, term), *tail]:
            t = '' if term is None else f' ≡ {show(term, tail)}'
            return f'{show_context(tail)}{var} : {show(type, tail)}{t}\n'

        case _:
            return ''


def type_check(expr: Expr, ctx: Context = []) -> Expr:
    match expr:
        case App(fun, arg):
            match value(type_check(fun, ctx), ctx):
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
                        f'\n{show_context(ctx)}Expecting a function, found {show(fun, ctx)} : {show(other, ctx)}'
                    )

        case Lam(var, type, body):
            type_check(type, ctx)

            return Pi(
                var,
                type,
                type_check(body, [(var, type, None), *ctx]),
            )

        case Let(var, term, body):
            type = type_check(term, ctx)
            return type_check(body, [(var, type, term), *ctx])

        case Pi(var, type, body):
            type_check(type, ctx)
            type_check(body, [(var, type, None), *ctx])
            return Unknown()

        case Unknown():
            return expr

        case Var(index):
            _, type, _ = ctx[index]
            return shift(type, index + 1)


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

        case Let(_, term, body):
            return eval(body, [eval(term, env), *env])

        case Pi(_, _, _):
            return None

        case Unknown():
            return None

        case Var(index):
            return env[index]
