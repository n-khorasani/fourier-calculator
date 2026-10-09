
import math
import ast
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.title("Fourier Series Calculator")
st.write("Enter x values as numbers or expressions such as pi/4, -pi/2, 2*pi.")

def parse_x(value):
    value = str(value).strip().lower()
    value = value.replace("π", "pi")
    value = re.sub(r"\bpi\b", "(pi)", value)

    allowed = {
        "pi": math.pi,
        "e": math.e,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in allowed:
            return allowed[node.id]
        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                return left ** right
        if isinstance(node, ast.UnaryOp):
            val = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -val
            if isinstance(node.op, ast.UAdd):
                return val
        raise ValueError("Unsupported expression")

    return evaluate(ast.parse(value, mode="eval"))


N = st.number_input("Number of points", 2, 100, 5, step=1)
H = st.number_input("Number of harmonics", 1, 50, 3, step=1)

st.write("Enter the coordinates of your points:")
data = pd.DataFrame({
    "x": ["0" if i == 0 else str(i) for i in range(N)],
    "f(x)": [0.0 for _ in range(N)]
})

data = st.data_editor(data, num_rows="fixed", key="points")

if st.button("Calculate Fourier Series"):
    try:
        x = [parse_x(value) for value in data["x"]]
        y = [float(value) for value in data["f(x)"]]

        if len(set(x)) != N:
            st.error("The x values must be different.")
        else:
            a0 = sum(y) / N
            a, b = [], []

            for n in range(1, H + 1):
                a.append(2 * sum(
                    y[i] * math.cos(n * x[i]) for i in range(N)
                ) / N)
                b.append(2 * sum(
                    y[i] * math.sin(n * x[i]) for i in range(N)
                ) / N)

            formula = f"f(x) = {a0:.4f}"
            for n in range(H):
                formula += f" + ({a[n]:.4f}) cos({n+1}x)"
                formula += f" + ({b[n]:.4f}) sin({n+1}x)"

            st.subheader("Fourier Series")
            st.code(formula)

            xg = [
                min(x) + (max(x) - min(x)) * j / 499
                for j in range(500)
            ]
            yg = [
                a0 + sum(
                    a[n] * math.cos((n+1)*xx)
                    + b[n] * math.sin((n+1)*xx)
                    for n in range(H)
                )
                for xx in xg
            ]

            fig, ax = plt.subplots()
            ax.plot(xg, yg, label="Fourier Series")
            ax.scatter(x, y, color="red", label="Input Points")
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    except Exception as error:
        st.error(f"Invalid input. Check your x values and f(x) values. Details: {error}")