from frontend.stmt_inferrer import *
import ast
import sys
import time

r = open("tests/inference/test.py")
t = ast.parse(r.read())
r.close()

solver = z3_types.TypesSolver(t)

context = Context()
solver.infer_stubs(context, infer)

for stmt in t.body:
    infer(stmt, context, solver)

solver.push()


def print_complete_solver(z3solver):
    pp = z3_types.z3printer._PP
    pp.max_lines = 4000
    pp.max_width = 120
    formatter = z3_types.z3printer._Formatter
    formatter.max_visited = 100000
    formatter.max_depth = 50
    formatter.max_args = 512
    out = sys.stdout
    pp(out, formatter(z3solver))


def print_context(ctx, ind=""):
    for v in sorted(ctx.types_map):
        z3_t = ctx.types_map[v]
        if isinstance(z3_t, (Context, AnnotatedFunction)):
            continue
        print(ind + "{}: {}".format(v, model[z3_t]))
        if ctx.has_context_in_children(v):
            print_context(ctx.get_context_from_children(v), "\t" + ind)
        if not ind:
            print("---------------------------")
    children = False
    for child in ctx.children_contexts:
        if ctx.name == "" and child.name == "":
            children = True
            print_context(child, "\t" + ind)
    if not ind and children:
        print("---------------------------")


start_time = time.time()
check = solver.optimize.check()
end_time = time.time()

if check == z3_types.unsat:
    print("Check: unsat")
    solver.check(solver.assertions_vars)
    print(solver.unsat_core())
    print([solver.assertions_errors[x] for x in solver.unsat_core()])
else:
    model = solver.optimize.model()
    print_context(context)

print("Ran in {} seconds".format(end_time - start_time))
