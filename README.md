# NEM_constraints
Python functions for wrangling public NEMDE constraint equation formulations:

- **get_constraint_list**: get a list of constraints from the archive for a specific month/year
- **find_constraint**: search for a specific constraint equation
- **get_LHS_terms**: get the left-hand side (LHS) terms of a specific constraint equation
- **get_RHS_terms**: get the right-hand side (RHS) terms of a specific constraint equation
- **get_constraint_details**: get the description, LHS and RHS terms of a specific constraint equation
- **find_generic_RHS_func**: find a generic RHS function definition from the archive
- **get_generic_RHS_func**: get the terms for a generic RHS function

## More Information
AEMO provides a lot of reference information on constraints, including the following:

- [MMS Data Model Reports](https://visualisations.aemo.com.au/aemo/di-help/Content/Data_Model/MMS_Data_Model.htm?TocPath=_____8)
- [Congestion Information Resource (CIR))](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/system-operations/congestion-information-resource) provides quite a bit of reference information, including: 
    - [Constraint Implementation Guidelines](https://www.aemo.com.au/-/media/files/stakeholder_consultation/consultations/nem-consultations/2023/constraints-implementation-guidelines/final-constraint-implementation-guidelines-v3.pdf?la=en)) which has details on the RHS data types and reverse polish notation calculation engine
    - [Constraint Formulation Guidelines](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/congestion-information/2021/constraint-formulation-guidelines.pdf?la=en) which has details on the relevant MMS tables and principles for formulating constraints
    - [Constraint Naming Guidelines](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/congestion-information/2016/constraint-naming-guidelines.pdf)