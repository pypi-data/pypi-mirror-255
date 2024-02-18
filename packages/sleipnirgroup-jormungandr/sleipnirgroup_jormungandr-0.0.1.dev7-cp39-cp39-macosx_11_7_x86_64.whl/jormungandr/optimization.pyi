from __future__ import annotations
import _jormungandr.autodiff
import typing
__all__ = ['EqualityConstraints', 'InequalityConstraints', 'OptimizationProblem', 'SolverExitCondition', 'SolverIterationInfo', 'SolverStatus']
class EqualityConstraints:
    """
    A vector of equality constraints of the form cₑ(x) = 0.
    """
    def __bool__(self) -> bool:
        """
        Implicit conversion operator to bool.
        """
class InequalityConstraints:
    """
    A vector of inequality constraints of the form cᵢ(x) ≥ 0.
    """
    def __bool__(self) -> bool:
        """
        Implicit conversion operator to bool.
        """
class OptimizationProblem:
    """
    This class allows the user to pose a constrained nonlinear
    optimization problem in natural mathematical notation and solve it.
    
    This class supports problems of the form: @verbatim minₓ f(x) subject
    to cₑ(x) = 0 cᵢ(x) ≥ 0 @endverbatim
    
    where f(x) is the scalar cost function, x is the vector of decision
    variables (variables the solver can tweak to minimize the cost
    function), cᵢ(x) are the inequality constraints, and cₑ(x) are the
    equality constraints. Constraints are equations or inequalities of the
    decision variables that constrain what values the solver is allowed to
    use when searching for an optimal solution.
    
    The nice thing about this class is users don't have to put their
    system in the form shown above manually; they can write it in natural
    mathematical form and it'll be converted for them. We'll cover some
    examples next.
    
    ## Double integrator minimum time
    
    A system with position and velocity states and an acceleration input
    is an example of a double integrator. We want to go from 0 m at rest
    to 10 m at rest in the minimum time while obeying the velocity limit
    (-1, 1) and the acceleration limit (-1, 1).
    
    The model for our double integrator is ẍ=u where x is the vector
    [position; velocity] and u is the acceleration. The velocity
    constraints are -1 ≤ x(1) ≤ 1 and the acceleration constraints are -1
    ≤ u ≤ 1.
    
    ### Initializing a problem instance
    
    First, we need to make a problem instance.
    
    ```
    {.cpp}
     #include <Eigen/Core>
     #include <sleipnir/optimization/OptimizationProblem.hpp>
    
     int main() {
       constexpr auto T = 5s;
       constexpr auto dt = 5ms;
       constexpr int N = T / dt;
    
       sleipnir::OptimizationProblem problem;
    ```
    
    ### Creating decision variables
    
    First, we need to make decision variables for our state and input.
    
    ```
    {.cpp}
       // 2x1 state vector with N + 1 timesteps (includes last state)
       auto X = problem.DecisionVariable(2, N + 1);
    
       // 1x1 input vector with N timesteps (input at last state doesn't matter)
       auto U = problem.DecisionVariable(1, N);
    ```
    
    By convention, we use capital letters for the variables to designate
    matrices.
    
    ### Applying constraints
    
    Now, we need to apply dynamics constraints between timesteps.
    
    ```
    {.cpp}
     // Kinematics constraint assuming constant acceleration between timesteps
     for (int k = 0; k < N; ++k) {
       constexpr double t = std::chrono::duration<double>(dt).count();
       auto p_k1 = X(0, k + 1);
       auto v_k1 = X(1, k + 1);
       auto p_k = X(0, k);
       auto v_k = X(1, k);
       auto a_k = U(0, k);
    
       // pₖ₊₁ = pₖ + vₖt
       problem.SubjectTo(p_k1 == p_k + v_k * t);
    
       // vₖ₊₁ = vₖ + aₖt
       problem.SubjectTo(v_k1 == v_k + a_k * t);
     }
    ```
    
    Next, we'll apply the state and input constraints.
    
    ```
    {.cpp}
     // Start and end at rest
     problem.SubjectTo(X.Col(0) == Eigen::Matrix<double, 2, 1>{{0.0}, {0.0}});
     problem.SubjectTo(
       X.Col(N + 1) == Eigen::Matrix<double, 2, 1>{{10.0}, {0.0}});
    
     // Limit velocity
     problem.SubjectTo(-1 <= X.Row(1));
     problem.SubjectTo(X.Row(1) <= 1);
    
     // Limit acceleration
     problem.SubjectTo(-1 <= U);
     problem.SubjectTo(U <= 1);
    ```
    
    ### Specifying a cost function
    
    Next, we'll create a cost function for minimizing position error.
    
    ```
    {.cpp}
     // Cost function - minimize position error
     sleipnir::Variable J = 0.0;
     for (int k = 0; k < N + 1; ++k) {
       J += sleipnir::pow(10.0 - X(0, k), 2);
     }
     problem.Minimize(J);
    ```
    
    The cost function passed to Minimize() should produce a scalar output.
    
    ### Solving the problem
    
    Now we can solve the problem.
    
    ```
    {.cpp}
     problem.Solve();
    ```
    
    The solver will find the decision variable values that minimize the
    cost function while satisfying the constraints.
    
    ### Accessing the solution
    
    You can obtain the solution by querying the values of the variables
    like so.
    
    ```
    {.cpp}
     double position = X.Value(0, 0);
     double velocity = X.Value(1, 0);
     double acceleration = U.Value(0);
    ```
    
    ### Other applications
    
    In retrospect, the solution here seems obvious: if you want to reach
    the desired position in the minimum time, you just apply positive max
    input to accelerate to the max speed, coast for a while, then apply
    negative max input to decelerate to a stop at the desired position.
    Optimization problems can get more complex than this though. In fact,
    we can use this same framework to design optimal trajectories for a
    drivetrain while satisfying dynamics constraints, avoiding obstacles,
    and driving through points of interest.
    
    ## Optimizing the problem formulation
    
    Cost functions and constraints can have the following orders:
    
    * none (i.e., there is no cost function or are no constraints)
    
    * constant
    
    * linear
    
    * quadratic
    
    * nonlinear
    
    For nonlinear problems, the solver calculates the Hessian of the cost
    function and the Jacobians of the constraints at each iteration.
    However, problems with lower order cost functions and constraints can
    be solved faster. For example, the following only need to be computed
    once because they're constant:
    
    * the Hessian of a quadratic or lower cost function
    
    * the Jacobian of linear or lower constraints
    
    A problem is constant if:
    
    * the cost function is constant or lower
    
    * the equality constraints are constant or lower
    
    * the inequality constraints are constant or lower
    
    A problem is linear if:
    
    * the cost function is linear
    
    * the equality constraints are linear or lower
    
    * the inequality constraints are linear or lower
    
    A problem is quadratic if:
    
    * the cost function is quadratic
    
    * the equality constraints are linear or lower
    
    * the inequality constraints are linear or lower
    
    All other problems are nonlinear.
    """
    def __init__(self) -> None:
        """
        Construct the optimization problem.
        """
    def callback(self, arg0: typing.Callable[[SolverIterationInfo], bool]) -> None:
        """
        Sets a callback to be called at each solver iteration.
        
        The callback for this overload should return bool.
        
        Parameter ``callback``:
            The callback. Returning true from the callback causes the solver
            to exit early with the solution it has so far.
        """
    @typing.overload
    def decision_variable(self) -> _jormungandr.autodiff.Variable:
        """
        Create a decision variable in the optimization problem.
        """
    @typing.overload
    def decision_variable(self, rows: int, cols: int = 1) -> _jormungandr.autodiff.VariableMatrix:
        """
        Create a matrix of decision variables in the optimization problem.
        
        Parameter ``rows``:
            Number of matrix rows.
        
        Parameter ``cols``:
            Number of matrix columns.
        """
    @typing.overload
    def maximize(self, arg0: _jormungandr.autodiff.Variable) -> None:
        """
        Tells the solver to maximize the output of the given objective
        function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``objective``:
            The objective function to maximize.
        """
    @typing.overload
    def maximize(self, arg0: _jormungandr.autodiff.VariableMatrix) -> None:
        """
        Tells the solver to maximize the output of the given objective
        function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``objective``:
            The objective function to maximize.
        """
    @typing.overload
    def maximize(self, arg0: float) -> None:
        """
        Tells the solver to maximize the output of the given objective
        function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``objective``:
            The objective function to maximize.
        """
    @typing.overload
    def minimize(self, arg0: _jormungandr.autodiff.Variable) -> None:
        """
        Tells the solver to minimize the output of the given cost function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``cost``:
            The cost function to minimize.
        """
    @typing.overload
    def minimize(self, arg0: _jormungandr.autodiff.VariableMatrix) -> None:
        """
        Tells the solver to minimize the output of the given cost function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``cost``:
            The cost function to minimize.
        """
    @typing.overload
    def minimize(self, arg0: float) -> None:
        """
        Tells the solver to minimize the output of the given cost function.
        
        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.
        
        Parameter ``cost``:
            The cost function to minimize.
        """
    def solve(self, **kwargs) -> SolverStatus:
        """
        Solve the optimization problem. The solution will be stored in the
        original variables used to construct the problem.
        
        Parameter ``config``:
            Configuration options for the solver.
        """
    @typing.overload
    def subject_to(self, arg0: EqualityConstraints) -> None:
        """
        Tells the solver to solve the problem while satisfying the given
        equality constraint.
        
        Parameter ``constraint``:
            The constraint to satisfy.
        """
    @typing.overload
    def subject_to(self, arg0: InequalityConstraints) -> None:
        """
        Tells the solver to solve the problem while satisfying the given
        inequality constraint.
        
        Parameter ``constraint``:
            The constraint to satisfy.
        """
    def symmetric_decision_variable(self, rows: int) -> _jormungandr.autodiff.VariableMatrix:
        """
        Create a symmetric matrix of decision variables in the optimization
        problem.
        
        Variable instances are reused across the diagonal, which helps reduce
        problem dimensionality.
        
        Parameter ``rows``:
            Number of matrix rows.
        """
class SolverExitCondition:
    """
    Solver exit condition.
    
    Members:
    
      SUCCESS : Solved the problem to the desired tolerance.
    
      SOLVED_TO_ACCEPTABLE_TOLERANCE : Solved the problem to an acceptable tolerance, but not the desired
    one.
    
      CALLBACK_REQUESTED_STOP : The solver returned its solution so far after the user requested a
    stop.
    
      TOO_FEW_DOFS : The solver determined the problem to be overconstrained and gave up.
    
      LOCALLY_INFEASIBLE : The solver determined the problem to be locally infeasible and gave
    up.
    
      FEASIBILITY_RESTORATION_FAILED : The solver failed to reach the desired tolerance, and feasibility
    restoration failed to converge.
    
      MAX_SEARCH_DIRECTION_TOO_SMALL : The solver failed to reach the desired tolerance due to the maximum
    search direction becoming too small.
    
      NONFINITE_INITIAL_COST_OR_CONSTRAINTS : The solver encountered nonfinite initial cost or constraints and gave
    up.
    
      DIVERGING_ITERATES : The solver encountered diverging primal iterates xₖ and/or sₖ and gave
    up.
    
      MAX_ITERATIONS_EXCEEDED : The solver returned its solution so far after exceeding the maximum
    number of iterations.
    
      MAX_WALL_CLOCK_TIME_EXCEEDED : The solver returned its solution so far after exceeding the maximum
    elapsed wall clock time.
    """
    CALLBACK_REQUESTED_STOP: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.CALLBACK_REQUESTED_STOP: 2>
    DIVERGING_ITERATES: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.DIVERGING_ITERATES: -6>
    FEASIBILITY_RESTORATION_FAILED: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.FEASIBILITY_RESTORATION_FAILED: -3>
    LOCALLY_INFEASIBLE: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.LOCALLY_INFEASIBLE: -2>
    MAX_ITERATIONS_EXCEEDED: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.MAX_ITERATIONS_EXCEEDED: -7>
    MAX_SEARCH_DIRECTION_TOO_SMALL: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.MAX_SEARCH_DIRECTION_TOO_SMALL: -4>
    MAX_WALL_CLOCK_TIME_EXCEEDED: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.MAX_WALL_CLOCK_TIME_EXCEEDED: -8>
    NONFINITE_INITIAL_COST_OR_CONSTRAINTS: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.NONFINITE_INITIAL_COST_OR_CONSTRAINTS: -5>
    SOLVED_TO_ACCEPTABLE_TOLERANCE: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.SOLVED_TO_ACCEPTABLE_TOLERANCE: 1>
    SUCCESS: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.SUCCESS: 0>
    TOO_FEW_DOFS: typing.ClassVar[SolverExitCondition]  # value = <SolverExitCondition.TOO_FEW_DOFS: -1>
    __members__: typing.ClassVar[dict[str, SolverExitCondition]]  # value = {'SUCCESS': <SolverExitCondition.SUCCESS: 0>, 'SOLVED_TO_ACCEPTABLE_TOLERANCE': <SolverExitCondition.SOLVED_TO_ACCEPTABLE_TOLERANCE: 1>, 'CALLBACK_REQUESTED_STOP': <SolverExitCondition.CALLBACK_REQUESTED_STOP: 2>, 'TOO_FEW_DOFS': <SolverExitCondition.TOO_FEW_DOFS: -1>, 'LOCALLY_INFEASIBLE': <SolverExitCondition.LOCALLY_INFEASIBLE: -2>, 'FEASIBILITY_RESTORATION_FAILED': <SolverExitCondition.FEASIBILITY_RESTORATION_FAILED: -3>, 'MAX_SEARCH_DIRECTION_TOO_SMALL': <SolverExitCondition.MAX_SEARCH_DIRECTION_TOO_SMALL: -4>, 'NONFINITE_INITIAL_COST_OR_CONSTRAINTS': <SolverExitCondition.NONFINITE_INITIAL_COST_OR_CONSTRAINTS: -5>, 'DIVERGING_ITERATES': <SolverExitCondition.DIVERGING_ITERATES: -6>, 'MAX_ITERATIONS_EXCEEDED': <SolverExitCondition.MAX_ITERATIONS_EXCEEDED: -7>, 'MAX_WALL_CLOCK_TIME_EXCEEDED': <SolverExitCondition.MAX_WALL_CLOCK_TIME_EXCEEDED: -8>}
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
class SolverIterationInfo:
    """
    Solver iteration information exposed to a user callback.
    """
    @property
    def A_e(self) -> scipy.sparse.csc_matrix:
        """
        The equality constraint Jacobian.
        """
    @property
    def A_i(self) -> scipy.sparse.csc_matrix:
        """
        The inequality constraint Jacobian.
        """
    @property
    def H(self) -> scipy.sparse.csc_matrix:
        """
        The Hessian of the Lagrangian.
        """
    @property
    def g(self) -> scipy.sparse.csc_matrix:
        """
        The gradient of the cost function.
        """
    @property
    def iteration(self) -> int:
        """
        The solver iteration.
        """
    @property
    def x(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        The decision variables.
        """
class SolverStatus:
    """
    Return value of OptimizationProblem::Solve() containing the cost
    function and constraint types and solver's exit condition.
    """
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, cost_function_type: _jormungandr.autodiff.ExpressionType = <ExpressionType.NONE: 0>, equality_constraint_type: _jormungandr.autodiff.ExpressionType = <ExpressionType.NONE: 0>, inequality_constraint_type: _jormungandr.autodiff.ExpressionType = <ExpressionType.NONE: 0>, exit_condition: SolverExitCondition = <SolverExitCondition.SUCCESS: 0>) -> None:
        ...
    @property
    def cost_function_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        The cost function type detected by the solver.
        """
    @cost_function_type.setter
    def cost_function_type(self, arg0: _jormungandr.autodiff.ExpressionType) -> None:
        ...
    @property
    def equality_constraint_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        The equality constraint type detected by the solver.
        """
    @equality_constraint_type.setter
    def equality_constraint_type(self, arg0: _jormungandr.autodiff.ExpressionType) -> None:
        ...
    @property
    def exit_condition(self) -> SolverExitCondition:
        """
        The solver's exit condition.
        """
    @exit_condition.setter
    def exit_condition(self, arg0: SolverExitCondition) -> None:
        ...
    @property
    def inequality_constraint_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        The inequality constraint type detected by the solver.
        """
    @inequality_constraint_type.setter
    def inequality_constraint_type(self, arg0: _jormungandr.autodiff.ExpressionType) -> None:
        ...
