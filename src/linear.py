"""
This file contains linear models for all optimizations
"""
import pyomo.environ as pyo
from .base import OptimizationModel  # ← relative import!


class GeneratorCommitment(OptimizationModel):
    """Unit commitment: minimize cost to meet demand."""
    
    def __init__(self, generators, gen_data, demand, **kwargs):
        """
        Args:
            generators: list of generator names
            gen_data: dict mapping gen name to {'fixed_cost', 'var_cost', 'capacity'}
            demand: total demand in MW
        """
        super().__init__(name="UnitCommitment", **kwargs)
        self.generators = generators
        self.gen_data = gen_data
        self.demand = demand
    
    def _create_sets_params(self):
        """Create sets and parameters for generators."""
        m = self.model
        m.GENERATORS = pyo.Set(initialize=self.generators)
        m.fixed_cost = pyo.Param(m.GENERATORS, 
                                 initialize={g: self.gen_data[g]['fixed_cost'] 
                                           for g in self.generators})
        m.var_cost = pyo.Param(m.GENERATORS, 
                               initialize={g: self.gen_data[g]['var_cost'] 
                                         for g in self.generators})
        m.capacity = pyo.Param(m.GENERATORS, 
                              initialize={g: self.gen_data[g]['capacity'] 
                                        for g in self.generators})
    
    def _create_variables(self):
        """Create binary on/off and continuous power variables."""
        m = self.model
        m.u = pyo.Var(m.GENERATORS, domain=pyo.Binary)  # on/off
        m.p = pyo.Var(m.GENERATORS, domain=pyo.NonNegativeReals)  # power
    
    def _create_objective(self):
        """Minimize total cost: fixed + variable."""
        m = self.model
        def obj_rule(mdl):
            return sum(mdl.fixed_cost[g] * mdl.u[g] + 
                       mdl.var_cost[g] * mdl.p[g] 
                       for g in mdl.GENERATORS)
        m.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)
    
    def _create_constraints(self):
        """Create capacity and demand constraints."""
        m = self.model
        
        def capacity_rule(mdl, g):
            return mdl.p[g] <= mdl.capacity[g] * mdl.u[g]
        
        m.capacity_constraint = pyo.Constraint(m.GENERATORS, rule=capacity_rule)
        
        def demand_rule(mdl):
            return sum(mdl.p[g] for g in mdl.GENERATORS) == self.demand
        
        m.demand_constraint = pyo.Constraint(rule=demand_rule)
    
    def print_results(self):
        """Print generator commitment results."""
        if self.result is None:
            print("Model not solved yet.")
            return
        
        self.print_solver_status()
        print(f"\nTotal Cost: ${self.get_objective_value():,.2f}\n")
        print("Generator Status:")
        for g in self.model.GENERATORS:
            u_val = self.model.u[g].value
            p_val = self.model.p[g].value
            cap = pyo.value(self.model.capacity[g])
            print(f"  {g}: on={u_val:.0f}, power={p_val:.1f}/{cap:.0f} MW")
        self.print_constraints_duals()