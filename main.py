from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from nat import Nat
from seq import Seq, Nil, lookup, Cons
from option import Some, Option


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


@dataclass(frozen=True)
class U:
    level: Nat = Nat(0)


@dataclass(frozen=True)
class Var:
    index: Nat


Expr = App | Lam | Pi | U | Var


Context = Seq[tuple[str, Expr]]


class Assoc(Enum):
    LEFT = 1
    RIGHT = 2
    BOTH = 3


def show(expr: Expr, ctx: Context = Nil(), assoc: Option[Assoc] = Some(Assoc.BOTH)) -> str:
    match expr:
        case App(fun, arg):
            result = f'{show(fun, ctx, Some(Assoc.LEFT))} {show(arg, ctx, None)}'

            match assoc:
                case Some(Assoc.LEFT | Assoc.BOTH):
                    return result

                case _:
                    return f'({result})'

        case Lam(var, type, body):
            result = f'λ ({var} : {show(type, ctx)}). {show(body, Cons((var, type), ctx))}'

            match assoc:
                case Some(Assoc.RIGHT | Assoc.BOTH):
                    return result

                case _:
                    return f'({result})'

        case Pi(var, type, body):
            result = f'Π ({var} : {show(type, ctx)}). {show(body, Cons((var, type), ctx))}'

            match assoc:
                case Some(Assoc.RIGHT | Assoc.BOTH):
                    return result

                case _:
                    return f'({result})'

        case U(level):
            return 'U' + chr(0x2080 + int(level))

        case Var(index):
            match lookup(index, ctx):
                case None:
                    raise Exception(
                        f'\n{show_context(ctx)}Out of bounds: {index}',
                    )

                case Some((name, _)):
                    return name


def shift(expr: Expr, n: int, cutoff: Nat = Nat(0)) -> Expr:
    match expr:
        case App(fun, arg):
            return App(shift(fun, n, cutoff), shift(arg, n, cutoff))

        case Lam(var, type, body):
            return Lam(var, shift(type, n, cutoff), shift(body, n, cutoff + Nat(1)))

        case Pi(var, type, body):
            return Pi(var, shift(type, n, cutoff), shift(body, n, cutoff + Nat(1)))

        case U(_):
            return expr

        case Var(index):
            if index < cutoff:
                return expr
            else:
                return Var(Nat(int(index) + n))


def substitute(expr: Expr, val: Expr, i: Nat = Nat(0)) -> Expr:
    match expr:
        case App(fun, arg):
            return App(substitute(fun, val, i), substitute(arg, val, i))

        case Lam(var, type, body):
            return Lam(
                var,
                substitute(type, val, i),
                substitute(body, shift(val, 1), i + Nat(1)),
            )

        case Pi(var, type, body):
            return Pi(
                var,
                substitute(type, val, i),
                substitute(body, shift(val, 1), i + Nat(1)),
            )

        case U(_):
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
        case Nil():
            return ''

        case Cons((var, type), tail):
            return f'{show_context(tail)}{var} : {show(type, tail)}\n'


def type_check(expr: Expr, ctx: Context = Nil()) -> Expr:
    match expr:
        case App(fun, arg):
            fun_type = type_check(fun, ctx)
            match fun_type:
                case Pi(var, type, body):
                    arg_type = type_check(arg, ctx)
                    match type_check(type, ctx):
                        case U(_):
                            pass

                        case other:
                            raise Exception(
                                f'\n{show_context(ctx)}Expecting a type, found {show(type, ctx)} : {show(other, ctx)}'
                            )

                    if arg_type != type:
                        raise Exception(
                            f'\n{show_context(ctx)}Expecting a {show(type, ctx)}, found {show(arg, ctx)} : {show(arg_type, ctx)}'
                        )

                    return shift(substitute(body, shift(arg, 1)), -1)

                case other:
                    raise Exception(
                        f'\n{show_context(ctx)}Expecting a function, found {show(other, ctx)} : {show(fun_type, ctx)}'
                    )

        case Lam(var, type, body):
            type_type = type_check(type, ctx)
            match type_type:
                case U(_):
                    return Pi(
                        var,
                        type,
                        type_check(body, Cons((var, type), ctx)),
                    )

                case other:
                    raise Exception(
                        f'\n{show_context(ctx)}Expecting a type, found {show(other, ctx)} : {show(type_type, ctx)}'
                    )

        case Pi(var, type, body):
            match type_check(type, ctx), type_check(body, Cons((var, type), ctx)):
                case U(l1), U(l2):
                    return U(max(l1, l2))

                case x, y:
                    raise Exception(
                        f'\n{show_context(ctx)}Assertion failed: {show(x, ctx)} == {show(y, ctx)}'
                    )

        case U(level):
            return U(level + Nat(1))

        case Var(index):
            match lookup(index, ctx):
                case None:
                    raise Exception(
                        f'\n{show_context(ctx)}Out of bounds: {index}'
                    )

                case Some((_, type)):
                    return shift(type, int(index) + 1)

        case _:
            raise Exception('TODO')
