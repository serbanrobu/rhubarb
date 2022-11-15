from main import *

ctx: Context = [
    ('C', Unknown(), None),
    ('B', Unknown(), None),
    ('A', Unknown(), None),
]

e = Lam(
    'bc',
    Pi('_', Var(1), Var(1)),
    Lam(
        'ab',
        Pi('_', Var(3), Var(3)),
        Lam(
            'a',
            Var(4),
            App(Var(2), App(Var(1), Var(0))),
        ),
    ),
)


def test_compose() -> None:
    type_check(e, ctx)


ctx = []

e = Lam('A', Unknown(), Lam('a', Var(0), Var(0)))


def test_id() -> None:
    type_check(e, ctx)


ctx = [
    (
        'snd',
        Pi(
            'B',
            Unknown(),
            Pi(
                '_',
                App(App(Var(3), Unknown()), Var(0)),
                Var(1),
            ),
        ),
        None,
    ),
    (
        'fst',
        Pi(
            'A',
            Unknown(),
            Pi(
                '_',
                App(App(Var(2), Var(0)), Unknown()),
                Var(1),
            ),
        ),
        None,
    ),
    (
        'pair',
        Pi(
            'A',
            Unknown(),
            Pi(
                'B',
                Unknown(),
                Pi(
                    '_',
                    Var(1),
                    Pi(
                        '_',
                        Var(1),
                        App(App(Var(4), Var(3)), Var(2)),
                    ),
                ),
            ),
        ),
        None,
    ),
    (
        'Pair',
        Pi('_', Unknown(), Pi('_', Unknown(), Unknown())),
        None,
    ),
]

e = Lam(
    'A',
    Unknown(),
    Lam(
        'B',
        Unknown(),
        Lam(
            'p',
            App(App(Var(5), Var(1)), Var(0)),
            App(
                App(
                    App(App(Var(5), Var(1)), Var(2)),
                    App(App(Var(3), Var(1)), Var(0)),
                ),
                App(App(Var(4), Var(2)), Var(0)),
            )
        ),
    ),
)


def test_swap() -> None:
    type_check(e, ctx)


ctx = [
    ('succ', Pi('_', Var(1), Var(2)), None),
    ('0', Var(0), None),
    ('Nat', Unknown(), None),
    *ctx,
]

one = App(Var(0), Var(1))
two = App(Var(0), one)
three = App(Var(0), two)

e = App(App(App(App(Var(5), Var(2)), Var(2)), three), two)


def test_swap_nat() -> None:
    type_check(e, ctx)


e1 = App(App(Var(4), Var(2)), e)


def test_nat_1() -> None:
    type_check(e1, ctx)


print(show(e1, ctx))


def succ(n: int) -> int:
    return n + 1


def fst(_: Any) -> Callable[[tuple[Any, Any]], Any]:
    return lambda p: p[0]


def snd(_: Any) -> Callable[[tuple[Any, Any]], Any]:
    return lambda p: p[1]


def pair(_: Any) -> Callable[[Any], Callable[[Any], Callable[[Any], tuple[Any, Any]]]]:
    return lambda _: lambda a: lambda b: (a, b)


env = [
    succ,
    0,
    None,  # Nat
    snd,
    fst,
    pair,
    None,  # Pair
]


def test_eval_nat_1() -> None:
    assert eval(e1, env) == 3


e2 = App(App(Var(3), Var(2)), e)


def test_nat_2() -> None:
    type_check(e2, ctx)


def test_eval_nat_2() -> None:
    assert eval(e2, env) == 2


def test_pq_nq_np() -> None:
    ctx = [
        (
            'Not',
            Pi('_', Unknown(), Unknown()),
            Lam('A', Unknown(), Pi('_', Var(0), Var(2))),
        ),
        ('Void', Unknown(), None),
    ]

    e = Lam(
        'P',
        Unknown(),
        Lam(
            'Q',
            Unknown(),
            Lam(
                'pq',
                Pi(
                    '_',
                    Var(1),  # P
                    Var(1),  # Q
                ),
                Lam(
                    'nq',
                    App(
                        Var(3),  # Not
                        Var(1),  # Q
                    ),
                    Lam(
                        'p',
                        Var(3),  # P
                        App(
                            Var(1),  # nq
                            App(
                                Var(2),  # pq
                                Var(0),  # p
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    type_check(e, ctx)
