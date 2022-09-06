import seq
from main import *


ctx: Context = seq.from_list([
    ('C', U()),
    ('B', U()),
    ('A', U()),
])

e = Lam(
    'bc',
    Pi('_', Var(Nat(1)), Var(Nat(1))),
    Lam(
        'ab',
        Pi('_', Var(Nat(3)), Var(Nat(3))),
        Lam(
            'a',
            Var(Nat(4)),
            App(Var(Nat(2)), App(Var(Nat(1)), Var(Nat(0)))),
        ),
    ),
)

print(f'{show_context(ctx)}{show(e, ctx)} : {show(type_check(e, ctx), ctx)}')

print()

ctx = Nil()

e = Lam('A', U(), Lam('a', Var(Nat(0)), Var(Nat(0))))

print(f'{show_context(ctx)}{show(e, ctx)} : {show(type_check(e, ctx), ctx)}')

print()

ctx = seq.from_list([
    (
        'snd',
        Pi(
            'A',
            U(),
            Pi(
                'B',
                U(),
                Pi(
                    '_',
                    App(App(Var(Nat(4)), Var(Nat(1))), Var(Nat(0))),
                    Var(Nat(1)),
                ),
            ),
        ),
    ),
    (
        'fst',
        Pi(
            'A',
            U(),
            Pi(
                'B',
                U(),
                Pi(
                    '_',
                    App(App(Var(Nat(3)), Var(Nat(1))), Var(Nat(0))),
                    Var(Nat(2)),
                ),
            ),
        ),
    ),
    (
        'pair',
        Pi(
            'A',
            U(),
            Pi(
                'B',
                U(),
                Pi(
                    '_',
                    Var(Nat(1)),
                    Pi(
                        '_',
                        Var(Nat(1)),
                        App(App(Var(Nat(4)), Var(Nat(3))), Var(Nat(2))),
                    ),
                ),
            ),
        ),
    ),
    ('Pair', Pi('_', U(), Pi('_', U(), U()))),
])

e = Lam(
    'A',
    U(),
    Lam(
        'B',
        U(),
        Lam(
            'p',
            App(App(Var(Nat(5)), Var(Nat(1))), Var(Nat(0))),
            App(
                App(
                    App(App(Var(Nat(5)), Var(Nat(1))), Var(Nat(2))),
                    App(App(App(Var(Nat(3)), Var(Nat(2))), Var(Nat(1))), Var(Nat(0))),
                ),
                App(App(App(Var(Nat(4)), Var(Nat(2))), Var(Nat(1))), Var(Nat(0))),
            )
        ),
    ),
)

print(f'{show_context(ctx)}{show(e, ctx)} : {show(type_check(e, ctx), ctx)}')

print()

ctx = Cons(
    ('succ', Pi('_', Var(Nat(1)), Var(Nat(2)))),
    Cons(
        ('zero', Var(Nat(0))),
        Cons(
            ('Nat', U()),
            ctx,
        ),
    ),
)

one = App(Var(Nat(0)), Var(Nat(1)))
two = App(Var(Nat(0)), one)
three = App(Var(Nat(0)), two)

e = App(App(Var(Nat(5)), U()), Var(Nat(2)))

print(f'{show_context(ctx)}{show(e, ctx)}')
# print(f'{show_context(ctx)}{show(e, ctx)} : {show(type_check(e, ctx), ctx)}')
