from __future__ import annotations
import _jormungandr.optimization
import typing
__all__ = ['ExpressionType', 'Gradient', 'Hessian', 'Jacobian', 'Variable', 'VariableBlock', 'VariableMatrix', 'abs', 'acos', 'asin', 'atan', 'atan2', 'block', 'cos', 'cosh', 'cwise_reduce', 'erf', 'exp', 'hypot', 'log', 'log10', 'pow', 'sign', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
class ExpressionType:
    """
    Expression type.
    
    Used for autodiff caching.
    
    Members:
    
      NONE : There is no expression.
    
      CONSTANT : The expression is a constant.
    
      LINEAR : The expression is composed of linear and lower-order operators.
    
      QUADRATIC : The expression is composed of quadratic and lower-order operators.
    
      NONLINEAR : The expression is composed of nonlinear and lower-order operators.
    """
    CONSTANT: typing.ClassVar[ExpressionType]  # value = <ExpressionType.CONSTANT: 1>
    LINEAR: typing.ClassVar[ExpressionType]  # value = <ExpressionType.LINEAR: 2>
    NONE: typing.ClassVar[ExpressionType]  # value = <ExpressionType.NONE: 0>
    NONLINEAR: typing.ClassVar[ExpressionType]  # value = <ExpressionType.NONLINEAR: 4>
    QUADRATIC: typing.ClassVar[ExpressionType]  # value = <ExpressionType.QUADRATIC: 3>
    __members__: typing.ClassVar[dict[str, ExpressionType]]  # value = {'NONE': <ExpressionType.NONE: 0>, 'CONSTANT': <ExpressionType.CONSTANT: 1>, 'LINEAR': <ExpressionType.LINEAR: 2>, 'QUADRATIC': <ExpressionType.QUADRATIC: 3>, 'NONLINEAR': <ExpressionType.NONLINEAR: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Gradient:
    """
    This class calculates the gradient of a a variable with respect to a
    vector of variables.
    
    The gradient is only recomputed if the variable expression is
    quadratic or higher order.
    """
    @typing.overload
    def __init__(self, arg0: Variable, arg1: Variable) -> None:
        """
        Constructs a Gradient object.
        
        Parameter ``variable``:
            Variable of which to compute the gradient.
        
        Parameter ``wrt``:
            Variable with respect to which to compute the gradient.
        """
    @typing.overload
    def __init__(self, arg0: Variable, arg1: sleipnir::VariableMatrix) -> None:
        """
        Constructs a Gradient object.
        
        Parameter ``variable``:
            Variable of which to compute the gradient.
        
        Parameter ``wrt``:
            Vector of variables with respect to which to compute the gradient.
        """
    def calculate(self) -> scipy.sparse.csc_matrix:
        """
        Calculates the gradient.
        """
    def update(self) -> None:
        """
        Updates the value of the variable.
        """
class Hessian:
    """
    This class calculates the Hessian of a variable with respect to a
    vector of variables.
    
    The gradient tree is cached so subsequent Hessian calculations are
    faster, and the Hessian is only recomputed if the variable expression
    is nonlinear.
    """
    def __init__(self, arg0: Variable, arg1: sleipnir::VariableMatrix) -> None:
        """
        Constructs a Hessian object.
        
        Parameter ``variable``:
            Variable of which to compute the Hessian.
        
        Parameter ``wrt``:
            Vector of variables with respect to which to compute the Hessian.
        """
    def calculate(self) -> scipy.sparse.csc_matrix:
        """
        Calculates the Hessian.
        """
    def update(self) -> None:
        """
        Updates the values of the gradient tree.
        """
class Jacobian:
    """
    This class calculates the Jacobian of a vector of variables with
    respect to a vector of variables.
    
    The Jacobian is only recomputed if the variable expression is
    quadratic or higher order.
    """
    def __init__(self, arg0: sleipnir::VariableMatrix, arg1: sleipnir::VariableMatrix) -> None:
        """
        Constructs a Jacobian object.
        
        Parameter ``variables``:
            Vector of variables of which to compute the Jacobian.
        
        Parameter ``wrt``:
            Vector of variables with respect to which to compute the Jacobian.
        """
    def calculate(self) -> scipy.sparse.csc_matrix:
        """
        Calculates the Jacobian.
        """
    def update(self) -> None:
        """
        Updates the values of the variables.
        """
class Variable:
    """
    An autodiff variable pointing to an expression node.
    """
    __hash__: typing.ClassVar[None] = None
    @typing.overload
    def __add__(self, arg0: float) -> Variable:
        ...
    @typing.overload
    def __add__(self, arg0: Variable) -> Variable:
        ...
    @typing.overload
    def __eq__(self, arg0: Variable) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __iadd__(self, arg0: float) -> Variable:
        """
        Variable-Variable compound addition operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __iadd__(self, arg0: Variable) -> Variable:
        """
        Variable-Variable compound addition operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __imul__(self, arg0: float) -> Variable:
        """
        Variable-Variable compound multiplication operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __imul__(self, arg0: Variable) -> Variable:
        """
        Variable-Variable compound multiplication operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a linear Variable with a value of zero.
        """
    @typing.overload
    def __init__(self, arg0: float) -> None:
        """
        Constructs a Variable from a double.
        
        Parameter ``value``:
            The value of the Variable.
        """
    @typing.overload
    def __init__(self, arg0: int) -> None:
        """
        Constructs a Variable from an int.
        
        Parameter ``value``:
            The value of the Variable.
        """
    @typing.overload
    def __isub__(self, arg0: float) -> Variable:
        """
        Variable-Variable compound subtraction operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __isub__(self, arg0: Variable) -> Variable:
        """
        Variable-Variable compound subtraction operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __itruediv__(self, arg0: float) -> Variable:
        """
        Variable-Variable compound division operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __itruediv__(self, arg0: Variable) -> Variable:
        """
        Variable-Variable compound division operator.
        
        Parameter ``rhs``:
            Operator right-hand side.
        """
    @typing.overload
    def __le__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __mul__(self, arg0: float) -> Variable:
        ...
    @typing.overload
    def __mul__(self, arg0: Variable) -> Variable:
        ...
    def __neg__(self) -> Variable:
        ...
    def __pos__(self) -> Variable:
        ...
    def __pow__(self, arg0: int) -> Variable:
        ...
    def __radd__(self, arg0: float) -> Variable:
        ...
    def __rmul__(self, arg0: float) -> Variable:
        ...
    def __rsub__(self, arg0: float) -> Variable:
        ...
    def __rtruediv__(self, arg0: float) -> Variable:
        ...
    @typing.overload
    def __sub__(self, arg0: float) -> Variable:
        ...
    @typing.overload
    def __sub__(self, arg0: Variable) -> Variable:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Variable:
        ...
    @typing.overload
    def __truediv__(self, arg0: Variable) -> Variable:
        ...
    @typing.overload
    def set(self, arg0: float) -> Variable:
        """
        Assignment operator for double.
        
        Parameter ``value``:
            The value of the Variable.
        """
    @typing.overload
    def set(self, arg0: int) -> Variable:
        """
        Assignment operator for int.
        
        Parameter ``value``:
            The value of the Variable.
        """
    @typing.overload
    def set_value(self, arg0: float) -> Variable:
        """
        Sets Variable's internal value.
        
        Parameter ``value``:
            The value of the Variable.
        """
    @typing.overload
    def set_value(self, arg0: int) -> Variable:
        """
        Sets Variable's internal value.
        
        Parameter ``value``:
            The value of the Variable.
        """
    def update(self) -> None:
        """
        Updates the value of this variable based on the values of its
        dependent variables.
        """
    def value(self) -> float:
        """
        Returns the value of this variable.
        """
class VariableBlock:
    """
    A submatrix of autodiff variables with reference semantics.
    
    Template parameter ``Mat``:
        The type of the matrix whose storage this class points to.
    """
    __hash__: typing.ClassVar[None] = None
    @typing.overload
    def __add__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous], arg0: VariableBlock) -> VariableMatrix:
        ...
    def __array_ufunc__(self, arg0: typing.Any, arg1: str, *args, **kwargs) -> typing.Any:
        ...
    @typing.overload
    def __eq__(self, arg0: VariableMatrix) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: VariableBlock) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: Variable) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: int) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: Variable) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: int) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> Variable:
        """
        Returns a scalar subblock at the given row.
        
        Parameter ``row``:
            The scalar subblock's row.
        """
    @typing.overload
    def __getitem__(self, arg0: tuple) -> typing.Any:
        """
        Returns a scalar subblock at the given row and column.
        
        Parameter ``row``:
            The scalar subblock's row.
        
        Parameter ``col``:
            The scalar subblock's column.
        """
    @typing.overload
    def __gt__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __init__(self, arg0: VariableMatrix) -> None:
        """
        Constructs a Variable block pointing to all of the given matrix.
        
        Parameter ``mat``:
            The matrix to which to point.
        """
    @typing.overload
    def __init__(self, arg0: VariableMatrix, arg1: int, arg2: int, arg3: int, arg4: int) -> None:
        """
        Constructs a Variable block pointing to a subset of the given matrix.
        
        Parameter ``mat``:
            The matrix to which to point.
        
        Parameter ``rowOffset``:
            The block's row offset.
        
        Parameter ``colOffset``:
            The block's column offset.
        
        Parameter ``blockRows``:
            The number of rows in the block.
        
        Parameter ``blockCols``:
            The number of columns in the block.
        """
    def __iter__(self) -> typing.Iterator:
        ...
    @typing.overload
    def __le__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    def __len__(self) -> int:
        """
        Returns number of rows in the matrix.
        """
    @typing.overload
    def __lt__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    def __matmul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> VariableMatrix:
        ...
    def __neg__(self) -> VariableMatrix:
        ...
    def __pow__(self, arg0: int) -> Variable:
        ...
    @typing.overload
    def __rmul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: float) -> VariableMatrix:
        ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: Variable) -> Variable:
        ...
    @typing.overload
    def __setitem__(self, arg0: tuple, arg1: typing.Any) -> None:
        ...
    @typing.overload
    def __sub__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous], arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __truediv__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> VariableMatrix:
        ...
    def col(self, arg0: int) -> VariableBlock:
        """
        Returns a column slice of the variable matrix.
        
        Parameter ``col``:
            The column to slice.
        """
    def cols(self) -> int:
        """
        Returns number of columns in the matrix.
        """
    def cwise_transform(self, arg0: typing.Callable[[Variable], Variable]) -> VariableMatrix:
        """
        Transforms the matrix coefficient-wise with an unary operator.
        
        Parameter ``unaryOp``:
            The unary operator to use for the transform operation.
        """
    def row(self, arg0: int) -> VariableBlock:
        """
        Returns a row slice of the variable matrix.
        
        Parameter ``row``:
            The row to slice.
        """
    def rows(self) -> int:
        """
        Returns number of rows in the matrix.
        """
    @typing.overload
    def set(self, arg0: float) -> None:
        """
        Assigns a double to the block.
        
        This only works for blocks with one row and one column.
        """
    @typing.overload
    def set(self, arg0: numpy.ndarray[numpy.float64[m, n]]) -> None:
        """
        Assigns an Eigen matrix to the block.
        """
    @typing.overload
    def set_value(self, arg0: float) -> None:
        """
        Assigns a double to the block.
        
        This only works for blocks with one row and one column.
        """
    @typing.overload
    def set_value(self, arg0: numpy.ndarray[numpy.float64[m, n]]) -> None:
        """
        Sets block's internal values.
        """
    @typing.overload
    def value(self, arg0: int, arg1: int) -> float:
        """
        Returns an element of the variable matrix.
        
        Parameter ``row``:
            The row of the element to return.
        
        Parameter ``col``:
            The column of the element to return.
        """
    @typing.overload
    def value(self, arg0: int) -> float:
        """
        Returns a row of the variable column vector.
        
        Parameter ``index``:
            The index of the element to return.
        """
    @typing.overload
    def value(self) -> numpy.ndarray[numpy.float64[m, n]]:
        """
        Returns the contents of the variable matrix.
        """
    @property
    def T(self) -> VariableMatrix:
        """
        Returns the transpose of the variable matrix.
        """
    @property
    def shape(self) -> tuple:
        ...
class VariableMatrix:
    """
    A matrix of autodiff variables.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def ones(arg0: int, arg1: int) -> VariableMatrix:
        """
        Returns a variable matrix filled with ones.
        
        Parameter ``rows``:
            The number of matrix rows.
        
        Parameter ``cols``:
            The number of matrix columns.
        """
    @staticmethod
    def zero(arg0: int, arg1: int) -> VariableMatrix:
        """
        Returns a variable matrix filled with zeroes.
        
        Parameter ``rows``:
            The number of matrix rows.
        
        Parameter ``cols``:
            The number of matrix columns.
        """
    @typing.overload
    def __add__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self: float, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __add__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    def __array_ufunc__(self, arg0: typing.Any, arg1: str, *args, **kwargs) -> typing.Any:
        ...
    @typing.overload
    def __eq__(self, arg0: VariableMatrix) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: Variable) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: int) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: Variable) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: float) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: int) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: VariableBlock) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __eq__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.EqualityConstraints:
        """
        Equality operator that returns an equality constraint for two
        Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __ge__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> Variable:
        """
        Returns a block pointing to the given row.
        
        Parameter ``row``:
            The block row.
        """
    @typing.overload
    def __getitem__(self, arg0: tuple) -> typing.Any:
        """
        Returns a block pointing to the given row and column.
        
        Parameter ``row``:
            The block row.
        
        Parameter ``col``:
            The block column.
        """
    @typing.overload
    def __gt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __gt__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs an empty VariableMatrix.
        """
    @typing.overload
    def __init__(self, arg0: int) -> None:
        """
        Constructs a VariableMatrix column vector with the given rows.
        
        Parameter ``rows``:
            The number of matrix rows.
        """
    @typing.overload
    def __init__(self, arg0: int, arg1: int) -> None:
        """
        Constructs a VariableMatrix with the given dimensions.
        
        Parameter ``rows``:
            The number of matrix rows.
        
        Parameter ``cols``:
            The number of matrix columns.
        """
    @typing.overload
    def __init__(self, arg0: list[list[float]]) -> None:
        """
        Constructs a scalar VariableMatrix from a nested list of doubles.
        
        This overload is for Python bindings only.
        
        Parameter ``list``:
            The nested list of Variables.
        """
    @typing.overload
    def __init__(self, arg0: list[list[Variable]]) -> None:
        """
        Constructs a scalar VariableMatrix from a nested list of Variables.
        
        This overload is for Python bindings only.
        
        Parameter ``list``:
            The nested list of Variables.
        """
    @typing.overload
    def __init__(self, arg0: Variable) -> None:
        """
        Constructs a scalar VariableMatrix from a Variable.
        """
    @typing.overload
    def __init__(self, arg0: VariableBlock) -> None:
        """
        Constructs a VariableMatrix from a VariableBlock.
        """
    def __iter__(self) -> typing.Iterator:
        ...
    @typing.overload
    def __itruediv__(self, arg0: Variable) -> VariableMatrix:
        """
        Compound matrix division-assignment operator (only enabled when rhs is
        a scalar).
        
        Parameter ``rhs``:
            Variable to divide.
        """
    @typing.overload
    def __itruediv__(self, arg0: float) -> VariableMatrix:
        """
        Compound matrix division-assignment operator (only enabled when rhs is
        a scalar).
        
        Parameter ``rhs``:
            Variable to divide.
        """
    @typing.overload
    def __le__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than-or-equal-to comparison operator that returns an
        inequality constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __le__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than-or-equal-to comparison operator that returns an inequality
        constraint for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    def __len__(self) -> int:
        """
        Returns number of rows in the matrix.
        """
    @typing.overload
    def __lt__(self, arg0: VariableMatrix) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: Variable) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: float) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: int) -> _jormungandr.optimization.InequalityConstraints:
        """
        Greater-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: VariableBlock) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __lt__(self, arg0: numpy.ndarray[numpy.float64]) -> _jormungandr.optimization.InequalityConstraints:
        """
        Less-than comparison operator that returns an inequality constraint
        for two Variables.
        
        Parameter ``lhs``:
            Left-hand side.
        
        Parameter ``rhs``:
            Left-hand side.
        """
    @typing.overload
    def __matmul__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __matmul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> VariableMatrix:
        ...
    @typing.overload
    def __mul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    def __neg__(self) -> VariableMatrix:
        ...
    def __pow__(self, arg0: int) -> Variable:
        ...
    @typing.overload
    def __radd__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __radd__(self, arg0: float) -> VariableMatrix:
        ...
    @typing.overload
    def __radd__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: float) -> VariableMatrix:
        ...
    @typing.overload
    def __rmul__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __rsub__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __rsub__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: Variable) -> Variable:
        ...
    @typing.overload
    def __setitem__(self, arg0: tuple, arg1: typing.Any) -> None:
        ...
    @typing.overload
    def __sub__(self, arg0: VariableMatrix) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self, arg0: numpy.ndarray[numpy.float64[m, n], numpy.ndarray.flags.f_contiguous]) -> VariableMatrix:
        ...
    @typing.overload
    def __sub__(self, arg0: VariableBlock) -> VariableMatrix:
        ...
    @typing.overload
    def __truediv__(self, arg0: Variable) -> VariableMatrix:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> VariableMatrix:
        ...
    def col(self, arg0: int) -> VariableBlock:
        """
        Returns a column slice of the variable matrix.
        
        Parameter ``col``:
            The column to slice.
        """
    def cols(self) -> int:
        """
        Returns number of columns in the matrix.
        """
    def cwise_transform(self, arg0: typing.Callable[[Variable], Variable]) -> VariableMatrix:
        """
        Transforms the matrix coefficient-wise with an unary operator.
        
        Parameter ``unaryOp``:
            The unary operator to use for the transform operation.
        """
    def row(self, arg0: int) -> VariableBlock:
        """
        Returns a row slice of the variable matrix.
        
        Parameter ``row``:
            The row to slice.
        """
    def rows(self) -> int:
        """
        Returns number of rows in the matrix.
        """
    def set(self, arg0: numpy.ndarray[numpy.float64[m, n]]) -> None:
        """
        Assigns an Eigen matrix to a VariableMatrix.
        """
    def set_value(self, arg0: numpy.ndarray[numpy.float64[m, n]]) -> None:
        """
        Sets the VariableMatrix's internal values.
        """
    @typing.overload
    def value(self, arg0: int, arg1: int) -> float:
        """
        Returns an element of the variable matrix.
        
        Parameter ``row``:
            The row of the element to return.
        
        Parameter ``col``:
            The column of the element to return.
        """
    @typing.overload
    def value(self, arg0: int) -> float:
        """
        Returns a row of the variable column vector.
        
        Parameter ``index``:
            The index of the element to return.
        """
    @typing.overload
    def value(self) -> numpy.ndarray[numpy.float64[m, n]]:
        """
        Returns the contents of the variable matrix.
        """
    @property
    def T(self) -> VariableMatrix:
        """
        Returns the transpose of the variable matrix.
        """
    @property
    def shape(self) -> tuple:
        ...
@typing.overload
def abs(arg0: float) -> Variable:
    """
    std::abs() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def abs(arg0: Variable) -> Variable:
    """
    std::abs() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def acos(arg0: float) -> Variable:
    """
    std::acos() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def acos(arg0: Variable) -> Variable:
    """
    std::acos() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def asin(arg0: float) -> Variable:
    """
    std::asin() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def asin(arg0: Variable) -> Variable:
    """
    std::asin() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def atan(arg0: float) -> Variable:
    """
    std::atan() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def atan(arg0: Variable) -> Variable:
    """
    std::atan() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def atan2(arg0: float, arg1: Variable) -> Variable:
    """
    std::atan2() for Variables.
    
    Parameter ``y``:
        The y argument.
    
    Parameter ``x``:
        The x argument.
    """
@typing.overload
def atan2(arg0: Variable, arg1: float) -> Variable:
    """
    std::atan2() for Variables.
    
    Parameter ``y``:
        The y argument.
    
    Parameter ``x``:
        The x argument.
    """
@typing.overload
def atan2(arg0: Variable, arg1: Variable) -> Variable:
    """
    std::atan2() for Variables.
    
    Parameter ``y``:
        The y argument.
    
    Parameter ``x``:
        The x argument.
    """
def block(arg0: list[list[VariableMatrix]]) -> VariableMatrix:
    """
    Assemble a VariableMatrix from a nested list of blocks.
    
    Each row's blocks must have the same height, and the assembled block
    rows must have the same width. For example, for the block matrix [[A,
    B], [C]] to be constructible, the number of rows in A and B must
    match, and the number of columns in [A, B] and [C] must match.
    
    Parameter ``list``:
        The nested list of blocks.
    """
@typing.overload
def cos(arg0: float) -> Variable:
    """
    std::cos() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def cos(arg0: Variable) -> Variable:
    """
    std::cos() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def cosh(arg0: float) -> Variable:
    """
    std::cosh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def cosh(arg0: Variable) -> Variable:
    """
    std::cosh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def cwise_reduce(arg0: VariableMatrix, arg1: VariableMatrix, arg2: typing.Callable[[Variable, Variable], Variable]) -> VariableMatrix:
    """
    Applies a coefficient-wise reduce operation to two matrices.
    
    Parameter ``lhs``:
        The left-hand side of the binary operator.
    
    Parameter ``rhs``:
        The right-hand side of the binary operator.
    
    Parameter ``binaryOp``:
        The binary operator to use for the reduce operation.
    """
@typing.overload
def cwise_reduce(arg0: VariableBlock, arg1: VariableBlock, arg2: typing.Callable[[Variable, Variable], Variable]) -> VariableMatrix:
    """
    Applies a coefficient-wise reduce operation to two matrices.
    
    Parameter ``lhs``:
        The left-hand side of the binary operator.
    
    Parameter ``rhs``:
        The right-hand side of the binary operator.
    
    Parameter ``binaryOp``:
        The binary operator to use for the reduce operation.
    """
@typing.overload
def erf(arg0: float) -> Variable:
    """
    std::erf() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def erf(arg0: Variable) -> Variable:
    """
    std::erf() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def exp(arg0: float) -> Variable:
    """
    std::exp() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def exp(arg0: Variable) -> Variable:
    """
    std::exp() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def hypot(arg0: float, arg1: Variable) -> Variable:
    """
    std::hypot() for Variables.
    
    Parameter ``x``:
        The x argument.
    
    Parameter ``y``:
        The y argument.
    """
@typing.overload
def hypot(arg0: Variable, arg1: float) -> Variable:
    """
    std::hypot() for Variables.
    
    Parameter ``x``:
        The x argument.
    
    Parameter ``y``:
        The y argument.
    """
@typing.overload
def hypot(arg0: Variable, arg1: Variable) -> Variable:
    """
    std::hypot() for Variables.
    
    Parameter ``x``:
        The x argument.
    
    Parameter ``y``:
        The y argument.
    """
@typing.overload
def hypot(arg0: Variable, arg1: Variable, arg2: Variable) -> Variable:
    """
    std::hypot() for Variables.
    
    Parameter ``x``:
        The x argument.
    
    Parameter ``y``:
        The y argument.
    
    Parameter ``z``:
        The z argument.
    """
@typing.overload
def log(arg0: float) -> Variable:
    """
    std::log() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def log(arg0: Variable) -> Variable:
    """
    std::log() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def log10(arg0: float) -> Variable:
    """
    std::log10() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def log10(arg0: Variable) -> Variable:
    """
    std::log10() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def pow(arg0: float, arg1: Variable) -> Variable:
    """
    std::pow() for Variables.
    
    Parameter ``base``:
        The base.
    
    Parameter ``power``:
        The power.
    """
@typing.overload
def pow(arg0: Variable, arg1: float) -> Variable:
    """
    std::pow() for Variables.
    
    Parameter ``base``:
        The base.
    
    Parameter ``power``:
        The power.
    """
@typing.overload
def pow(arg0: Variable, arg1: Variable) -> Variable:
    """
    std::pow() for Variables.
    
    Parameter ``base``:
        The base.
    
    Parameter ``power``:
        The power.
    """
@typing.overload
def sign(arg0: float) -> Variable:
    """
    sign() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sign(arg0: Variable) -> Variable:
    """
    sign() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sin(arg0: float) -> Variable:
    """
    std::sin() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sin(arg0: Variable) -> Variable:
    """
    std::sin() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sinh(arg0: float) -> Variable:
    """
    std::sinh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sinh(arg0: Variable) -> Variable:
    """
    std::sinh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sqrt(arg0: float) -> Variable:
    """
    std::sqrt() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def sqrt(arg0: Variable) -> Variable:
    """
    std::sqrt() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def tan(arg0: float) -> Variable:
    """
    std::tan() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def tan(arg0: Variable) -> Variable:
    """
    std::tan() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def tanh(arg0: float) -> Variable:
    """
    std::tanh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
@typing.overload
def tanh(arg0: Variable) -> Variable:
    """
    std::tanh() for Variables.
    
    Parameter ``x``:
        The argument.
    """
