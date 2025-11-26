import polars 
import pyomo.environ as pyo
import numpy
from abc import ABC, abstractmethod

# create the first model
# This

class OptimizationModel(ABC):
    """
    Abstract Base Class for any optimization model created later
    Solves a general optimization model with constraints  
    """

    def __init__(self, solver_name='cbc', name='OptModel'):
        self.solver_name = solver_name                  #The solver name to use for this
        self.solver = pyo.SolverFactory(solver_name)    # Initialize Pyomo with the solver

        if not self.solver.available():     
            raise RuntimeError(f"Solver '{solver_name}' is not installed or not available.")    # check to ensure that the solver is available

        self.model = pyo.ConcreteModel(name=name)
        self.model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)
        self.result = None

    @abstractmethod
    def _create_sets_params(self):
        """Define all sets and parameters. Must be implemented by subclass."""
        pass
    
    @abstractmethod
    def _create_variables(self):
        """Define all decision variables. Must be implemented by subclass."""
        pass
    
    @abstractmethod
    def _create_objective(self):
        """Define objective function. Must be implemented by subclass."""
        pass
    
    @abstractmethod
    def _create_constraints(self):
        """Define all constraints. Must be implemented by subclass."""
        pass

    def build(self):
        """Build the complete model by calling all component creators."""
        self._create_sets_params()
        self._create_variables()
        self._create_objective()
        self._create_constraints()
        return self
    
    def solve(self, tee=True):
        """
        Solve the model.
        
        Args:
            tee: if True, print solver output
        
        Returns:
            self (for method chaining)
        """
        if self.model.is_constructed() is False:
            self.build()
        self.result = self.solver.solve(self.model, tee=tee)
        return self
    
    def print_solver_status(self):
        """Print solver result status."""
        if self.result is None:
            print("Model not solved yet.")
            return
        print(self.result)
    
    def get_objective_value(self):
        """Get objective function value."""
        try:
            return pyo.value(self.model.obj)
        except:
            return None
    

    def print_constraints_duals(self):
        """Print all constraint dual values (shadow prices)."""
        if self.result is None:
            print("Model not solved yet.")
            return
        print("\nConstraint Duals (Shadow Prices):")
        for c in self.model.component_objects(pyo.Constraint, active=True):
            for idx in c:
                dual_val = self.model.dual[c[idx]]
                print(f"  {c.name}[{idx}] = {dual_val}")


